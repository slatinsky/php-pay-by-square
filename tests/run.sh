#!/usr/bin/env bash
# Starts the app in Docker and runs tests/test_qr.py against it.
# Builds the app from the repository Dockerfile, or set IMAGE to test an existing image.
# Extra arguments are passed to unittest, e.g. tests/run.sh PayloadTest
set -euo pipefail
cd "$(dirname "$0")/.."

name=square-test-$$
image=${IMAGE:-square-test}

if [ -z "${IMAGE:-}" ]; then
    docker build -t "$image" .
fi
docker build -q -t square-test-runner tests >/dev/null

cleanup() {
    docker rm -f "$name" >/dev/null 2>&1 || true
    docker network rm "$name" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker network create "$name" >/dev/null
docker run -d --name "$name" --network "$name" "$image" >/dev/null
echo "Testing $image with PHP $(docker exec "$name" php -r 'echo PHP_VERSION;')"
docker run --rm --network "$name" -e BASE_URL="http://$name" square-test-runner "$@"
