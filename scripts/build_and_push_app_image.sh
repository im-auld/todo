#!/usr/bin/env bash
#!/usr/bin/env bash
set -e

if [[ $# -lt 1 ]]; then
    echo "Usage: build_and_push_nginx.sh -t IMAGE_VERSION" >&2
    exit 1
fi

while getopts "v:p" OPTION
do
	case $OPTION in
		v | --version)
			new_tag=app-${OPTARG}
			echo "Using tag: app-$new_tag"
			docker build -t todo:"$new_tag" .
			docker tag todo:"$new_tag" imauld/todo:"$new_tag"
			echo "Built image: todo:$new_tag"
			;;
		p | --push)
			echo "Pushing image to DockerHub: todo:$new_tag"
			docker push imauld/todo:$new_tag
			;;
	esac
done
