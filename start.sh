#!/bin/bash

# Start FastAPI on port 8000
uvicorn main:app --host 0.0.0.0 --port 8000 &


# Wait for FastAPI to start
sleep 5


# Start Streamlit on port 8501
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
