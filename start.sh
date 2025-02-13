#!/bin/bash

# Start FastAPI backend in the background
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit frontend (exposed to the web)
streamlit run app.py --server.port $PORT --server.address 0.0.0.0