#!/bin/bash

# Start FastAPI backend
uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 300 &

# Wait for FastAPI to be available
until curl --output /dev/null --silent --head --fail http://$BACKEND_HOST:8000/; do
    echo "Waiting for FastAPI to start..."
    sleep 2
done


# Start Streamlit frontend
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
