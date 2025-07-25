import logging
import uuid

from fastapi import APIRouter
from google.protobuf.timestamp import to_datetime
from starlette.requests import Request

from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.api.types.processing_pb2 import ProcessingItemKey
from dev_observer.api.web.observations_pb2 import GetObservationResponse, GetObservationsResponse, \
    CreateProcessingItemRequest, CreateProcessingItemResponse, DeleteProcessingItemRequest, \
    DeleteProcessingItemResponse, GetProcessingResultsRequest, GetProcessingResultsResponse, \
    GetProcessingRunStatusResponse, GetProcessingItemsRequest, GetProcessingItemsResponse, \
    GetProcessingResultResponse
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock, pb_to_dict, parse_dict_pb

_log = logging.getLogger(__name__)


class ObservationsService:
    _observations: ObservationsProvider
    _store: StorageProvider
    _clock: Clock

    router: APIRouter

    def __init__(self, observations: ObservationsProvider, store: StorageProvider, clock: Clock = RealClock()):
        self._observations = observations
        self._store = store
        self._clock = clock
        self.router = APIRouter()

        self.router.add_api_route("/observations/kind/{kind}", self.list_by_kind, methods=["GET"])
        self.router.add_api_route("/observation/{kind}/{name}/{key}", self.get, methods=["GET"])
        self.router.add_api_route("/processing/items", self.add_processing_item, methods=["POST"])
        self.router.add_api_route("/processing/items/filter", self.get_filtered_processing_tems, methods=["POST"])
        self.router.add_api_route("/processing/items", self.delete_processing_item, methods=["DELETE"])
        self.router.add_api_route("/processing/results", self.get_processing_results, methods=["POST"])
        self.router.add_api_route("/processing/results/{result_id}", self.get_processing_result, methods=["GET"])
        self.router.add_api_route("/processing/requests/runs/{request_id}",
                                  self.get_processing_request_status, methods=["GET"])

    async def list_by_kind(self, kind: str):
        keys = await self._observations.list(kind=kind)
        return pb_to_dict(GetObservationsResponse(keys=keys))

    async def get(self, kind: str, name: str, key: str):
        _log.debug(s_("Observation requested", kind=kind, name=name, key=key))
        observation = await self._observations.get(ObservationKey(kind=kind, name=name, key=key.replace("|", "/")))
        return pb_to_dict(GetObservationResponse(observation=observation))

    async def add_processing_item(self, request: Request):
        req = parse_dict_pb(await request.json(), CreateProcessingItemRequest())
        _log.debug(s_("Adding processing item", req=req))
        next_process = self._clock.now() if req.process_immediately else None
        await self._store.create_processing_time(req.key, req.data, next_time=next_process)
        return pb_to_dict(CreateProcessingItemResponse())

    async def get_filtered_processing_tems(self, request: Request):
        req = parse_dict_pb(await request.json(), GetProcessingItemsRequest())
        _log.debug(s_("Fetching processing items", req=req))
        filter_type = req.WhichOneof("filter")
        if filter_type == "namespace":
            items = await self._store.get_processing_items(filter=req.filter)
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")
        return pb_to_dict(GetProcessingItemsResponse(items=items))

    async def delete_processing_item(self, request: Request):
        req = parse_dict_pb(await request.json(), DeleteProcessingItemRequest())
        _log.debug(s_("Deleting processing item", req=req))
        await self._store.delete_processing_item(req.key)
        return pb_to_dict(DeleteProcessingItemResponse())

    async def get_processing_results(self, request: Request):
        req = parse_dict_pb(await request.json(), GetProcessingResultsRequest())
        _log.debug(s_("Get processing results", req=req))
        results = await self._store.get_processing_results(
            to_datetime(req.from_date), to_datetime(req.to_date), req.filter)
        return pb_to_dict(GetProcessingResultsResponse(results=results))

    async def get_processing_result(self, result_id: str):
        _log.debug(s_("Get processing result", result_id=result_id))
        result = await self._store.get_processing_result(result_id)
        return pb_to_dict(GetProcessingResultResponse(result=result))

    async def get_processing_request_status(self, request_id: str):
        _log.debug(s_("Get processing status", request_id=request_id))
        # validating that request id is UUID
        uuid.UUID(request_id)
        item = await self._store.get_processing_time(ProcessingItemKey(request_id=request_id))
        result = await self._store.get_processing_result(request_id)
        return pb_to_dict(GetProcessingRunStatusResponse(item=item, result=result))
