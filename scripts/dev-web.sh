#!/usr/bin/env bash

set -ex
set -o pipefail

root=$(git rev-parse --show-toplevel)

cd "$root"/web/packages/api
npm link
cd "$root"/web/apps/dev-observer
npm link @devplan/contextify-api
npm run dev
