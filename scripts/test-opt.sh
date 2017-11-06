while getopts "t:p" OPTION
do
	case $OPTION in
		t | --tag)
			echo "Using tag: app-${OPTARG}"
			new_tag=app-${OPTARG}
			echo "Built image: todo:$new_tag"
			;;
		p | --push)
			echo "Pushing image to DockerHub: todo:$new_tag"
			;;
	esac
done