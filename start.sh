#!/bin/bash
uvicorn main:app --host 0.0.0.0 --port $PORT & streamlit run app.py --server.port 8501 --server.address 0.0.0.0
