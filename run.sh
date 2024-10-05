#!/bin/bash

# Define variables
IMAGE_NAME="personal-automation-api"
CONTAINER_NAME="personal-automation-api"
PORT=1621
ENV_FILE=".env"

# Function to build the Docker image
build_image() {
    echo "Building Docker image..."
    docker build -t $IMAGE_NAME .
}

# Function to run the Docker container
run_container() {
    echo "Running Docker container..."
    docker run -d --name $CONTAINER_NAME -p $PORT:$PORT --env-file $ENV_FILE $IMAGE_NAME
}

# Function to stop and remove the Docker container
stop_container() {
    echo "Stopping and removing Docker container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
}

# Function to view logs
view_logs() {
    echo "Viewing logs..."
    docker logs -f $CONTAINER_NAME
}

# Function to execute a shell inside the running container
exec_shell() {
    echo "Executing shell inside the container..."
    docker exec -it $CONTAINER_NAME /bin/bash
}

# Function to clean up dangling images
cleanup_images() {
    echo "Cleaning up dangling images..."
    docker image prune -f
}

# Function to build and run the Docker container
start_container() {
    echo "Building and running Docker container..."
    build_image

    # Check if the container is already running
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo "Container is already running. Stopping and removing it first..."
        stop_container
    elif [ "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
        # Cleanup if the container exists but is stopped
        echo "Removing stopped container..."
        docker rm $CONTAINER_NAME
    fi

    run_container

    # Print the URL and open the FastAPI docs page
    echo "API is running at http://localhost:$PORT"
    echo "Opening FastAPI docs..."
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:$PORT/docs"
    elif command -v open &> /dev/null; then
        open "http://localhost:$PORT/docs"
    else
        echo "Please open http://localhost:$PORT/docs in your browser."
    fi
}

# Display help
display_help() {
    echo "Usage: $0 {build|run|stop|logs|shell|cleanup|start|help}"
    echo "  build   - Build the Docker image"
    echo "  run     - Run the Docker container"
    echo "  stop    - Stop and remove the Docker container"
    echo "  logs    - View logs of the running container"
    echo "  shell   - Execute a shell inside the running container"
    echo "  cleanup - Clean up dangling Docker images"
    echo "  start   - Build and run the Docker container"
    echo "  help    - Display this help message"
}

# Main script logic
case "$1" in
    build)
        build_image
        ;;
    run)
        run_container
        ;;
    stop)
        stop_container
        ;;
    logs)
        view_logs
        ;;
    shell)
        exec_shell
        ;;
    cleanup)
        cleanup_images
        ;;
    start)
        start_container
        ;;
    help|*)
        display_help
        ;;
esac