#!/bin/bash

# Load variables from .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Configuration
PORT=8000
DOMAIN=${NGROK_DOMAIN:-""}

# Start the backend server in the background
echo "Starting FastAPI backend server on port $PORT..."
python main.py &
SERVER_PID=$!

# Wait for the server to start
sleep 3

# Start ngrok tunnel
echo "Starting ngrok tunnel..."
if [ -z "$DOMAIN" ]; then
  # No custom domain specified, use random ngrok URL
  ngrok http $PORT > ngrok.log 2>&1 &
else
  # Use custom domain
  ngrok http $PORT --domain=$DOMAIN > ngrok.log 2>&1 &
fi
NGROK_PID=$!

# Display the ngrok URL after a short delay
sleep 3
echo "====================================================="
echo "Agro-Bot API is now running at:"
echo "Local: http://localhost:$PORT"
echo "Ngrok tunnel is active. Check ngrok dashboard for URL."
echo "====================================================="

# Handle shutdown
cleanup() {
  echo "Shutting down..."
  kill $NGROK_PID 2>/dev/null
  kill $SERVER_PID 2>/dev/null
  exit 0
}

# Set up signal trapping
trap cleanup SIGINT SIGTERM

# Keep the script running
echo "Press Ctrl+C to stop the server"
wait $SERVER_PID 