#!/bin/bash
# run_tests.sh — Wait for the API to be healthy, then run pytest

echo "Waiting for API to be ready..."

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:3020/health | grep -q "healthy"; then
        echo "API is ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Attempt $RETRY_COUNT/$MAX_RETRIES - API not ready yet..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "API did not become ready in time. Exiting."
    exit 1
fi

echo ""
echo "Running tests..."
echo ""

cd tests && python -m pytest "$@"
