#!/bin/bash

# Start FastAPI backend
uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 300 &

# Wait for FastAPI to be available
echo "Waiting for FastAPI to start..."
while ! nc -z 0.0.0.0 8000; do   
  sleep 1
done
echo "FastAPI is running!"

# Start Streamlit frontend
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
