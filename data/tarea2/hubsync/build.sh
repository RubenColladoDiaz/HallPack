#!/bin/bash
# Build helper for hubsync. Usage: ./build.sh [-m]
TOOL_NAME="hubsync"
TOOL_VERSION="03.04.00"

if [ "$1" == "-m" ]; then
    cat CHANGELOG.ver
    exit 0
fi

echo "Building ${TOOL_NAME} ${TOOL_VERSION}..."
tar -czf "${TOOL_NAME}-${TOOL_VERSION}.tar.gz" src/ CHANGELOG.ver
