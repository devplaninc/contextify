import asyncio
import logging
import subprocess
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

import dev_observer
from dev_observer.log import s_

dev_observer.log.encoder = dev_observer.log.PlainTextEncoder()
logging.basicConfig(level=logging.DEBUG)

# Or suppress all AWS-related debug messages
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('aiobotocore').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)

from dev_observer.server import detect
from dev_observer.server.middleware.auth import AuthMiddleware
from dev_observer.server.services.config import ConfigService
from dev_observer.server.services.observations import ObservationsService
from dev_observer.server.services.repositories import RepositoriesService
from dev_observer.server.services.sites import WebSitesService
from dev_observer.server.services.tokens import TokensService

_log = logging.getLogger(__name__)

env = detect.env


def start_bg_processing():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(env.periodic_processor.run())


@asynccontextmanager
async def lifespan(_: FastAPI):
    thread = threading.Thread(target=start_bg_processing, daemon=True)
    thread.start()
    yield


app = FastAPI(lifespan=lifespan)

# Create auth middleware
auth_middleware = AuthMiddleware(env.users, env.api_keys)

# Create services
config_service = ConfigService(env.storage, env.users)
repos_service = RepositoriesService(env.storage, env.observations, env.prompts, env.analysis)
observations_service = ObservationsService(env.observations, env.storage)
websites_service = WebSitesService(env.storage)
tokens_service = TokensService(env.storage)

# Include routers with authentication
app.include_router(
    config_service.router,
    prefix="/api/v1",
    dependencies=[Depends(auth_middleware.verify_token)]
)
app.include_router(
    repos_service.router,
    prefix="/api/v1",
    dependencies=[Depends(auth_middleware.verify_token)]
)
app.include_router(
    observations_service.router,
    prefix="/api/v1",
    dependencies=[Depends(auth_middleware.verify_token)]
)
app.include_router(
    websites_service.router,
    prefix="/api/v1",
    dependencies=[Depends(auth_middleware.verify_token)]
)
app.include_router(
    tokens_service.router,
    prefix="/api/v1",
    dependencies=[Depends(auth_middleware.verify_token)]
)

origins = [
    "http://localhost:5173",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all origins (not recommended for prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def start_fastapi_server():
    import uvicorn
    port = 8090
    uvicorn_config = uvicorn.Config("dev_observer.server.main:app", host="0.0.0.0", port=port, log_level="debug")
    uvicorn_server = uvicorn.Server(uvicorn_config)
    _log.info(s_("Starting FastAPI server...", port=port))
    await uvicorn_server.serve()


def start_all():
    async def start():
        await start_fastapi_server()

    asyncio.run(start())


if __name__ == "__main__":
    start_all()


def _get_git_root() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout.strip()
