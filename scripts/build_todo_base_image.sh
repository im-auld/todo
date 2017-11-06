#!/usr/bin/env bash
set -x
set -e


if [[ $# -lt 1 ]]; then
    echo "Usage: build_and_push_nginx.sh IMAGE_TAG" >&2
    exit 1
fi

new_tag="base-$1"
echo new_tag

docker build -t todo:"$new_tag" -f Dockerfile.base .
docker tag todo:"$new_tag" imauld/todo:"$new_tag"
docker push imauld/todo:$new_tag

echo "Pushed image to Docker Hub: todo:$new_tag"
