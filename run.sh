#!/usr/bin/env bash

set -euo pipefail

# Define variables
readonly IMAGE_NAME="personal-automation-api"
readonly CONTAINER_NAME="personal-automation-api"
readonly PORT=1621
readonly ENV_FILE=".env"

# Helper functions
log() { echo "$(date +'%Y-%m-%d %H:%M:%S') $*" >&2; }
error() { log "ERROR: $*"; exit 1; }

# Docker operations
build_image() { docker build -t "$IMAGE_NAME" .; }
stop_container() { docker stop "$CONTAINER_NAME" 2>/dev/null || true; }
remove_container() { docker rm "$CONTAINER_NAME" 2>/dev/null || true; }
view_logs() { docker logs -f "$CONTAINER_NAME"; }
exec_shell() { docker exec -it "$CONTAINER_NAME" /bin/bash; }
cleanup_images() { docker image prune -f; }

run_container() {
    local detach_flag=${1:-}
    docker run $detach_flag --name "$CONTAINER_NAME" \
               -p "$PORT:$PORT" \
               --env-file "$ENV_FILE" \
               -v "$(pwd)/app:/app/app" \
               "$IMAGE_NAME" \
               uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
}

start_container() {
    local detach_flag=${1:-}
    build_image
    stop_container
    remove_container
    
    log "API is running at http://localhost:$PORT"
    open_browser "http://localhost:$PORT/docs" &
    
    run_container "$detach_flag"
}

open_browser() {
    local url=$1
    if command -v xdg-open &>/dev/null; then
        xdg-open "$url"
    elif command -v open &>/dev/null; then
        open "$url"
    else
        log "Please open $url in your browser."
    fi
}

display_help() {
    cat << EOF
Usage: $0 <command> [options]

Commands:
  build   - Build the Docker image
  run     - Run the Docker container
  stop    - Stop the Docker container
  logs    - View logs of the running container
  shell   - Execute a shell inside the running container
  cleanup - Clean up dangling Docker images
  start   - Build and run the Docker container with hot reloading

Options:
  -d      - Run in detached mode (applicable to 'run' and 'start' commands)

EOF
}

# Main execution
main() {
    local cmd=${1:-}
    local detach_flag=""

    [[ $# -eq 0 ]] && { display_help; exit 1; }

    if [[ "${2:-}" == "-d" ]]; then
        detach_flag="-d"
    fi

    case "$cmd" in
        build)   build_image ;;
        run)     run_container "$detach_flag" ;;
        stop)    stop_container ;;
        logs)    view_logs ;;
        shell)   exec_shell ;;
        cleanup) cleanup_images ;;
        start)   start_container "$detach_flag" ;;
        help)    display_help ;;
        *)       error "Unknown command: $cmd" ;;
    esac
}

main "$@"