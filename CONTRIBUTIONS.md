# dev-observer
Observer of all the important stuff.
Standalone context building application that performs in-depth github repository analysis and website crawl. Output is a summary that can be used for context in AI applications like Devplan or for input into other process (or simply for better understanding of code or website content).

## Setup:

Create file [server/.env.local.secrets](server/.env.local.secrets) and add following there:
```
DEV_OBSERVER__GIT__GITHUB__PERSONAL_TOKEN=<Github personal token, use `gh auth token` to get>
DEV_OBSERVER__GIT__GITHUB__PRIVATE_KEY=<GH private key if app auth is used>
DEV_OBSERVER__GIT__GITHUB__APP_ID="<GH APP ID if app auth is used>"
GOOGLE_API_KEY=<GOOGLE_API_TOKEN to use for google-genai>
DEV_OBSERVER__USERS_MANAGEMENT__CLERK__SECRET_KEY=<get key from Clerk>
```

### Building and Publishing Docker Images

#### Using GitHub Actions

Docker images can be built and published manually using the GitHub Actions workflow:

1. Go to the "Actions" tab in the GitHub repository
2. Select the "Build and Publish Docker Images" workflow
3. Click "Run workflow"
4. Enter a semantic version tag (e.g., `v1.0.0`)
5. Click "Run workflow"

The workflow will build both Docker images, tag them with the provided version, and publish them to GitHub Packages.

#### Building Locally

You can also build the Docker images locally:

```bash
# Navigate to the repository root
# Build the web frontend image
docker build -t contextify-web:local -f docker/web/Dockerfile .

# Build the server backend image
docker build -t contextify-server:local -f docker/server/Dockerfile .
```

Note that you must run these commands from the repository root directory, as the Dockerfiles reference files relative to this location.

# DB Upgrades
1. To upgrade local DB, run `make migration-apply`
2. To upgrade remote DB, run `DEV_OBSERVER_DB_URL=<CONNECTION_STRING> make migration-apply`

