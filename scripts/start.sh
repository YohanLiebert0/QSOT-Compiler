#!/bin/bash
# scripts/start.sh — Unified Launcher for API and Dashboard

# Add src to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# 1. Start API Server in background
echo "🔌 Starting QSOT API Server on port 8000..."
uvicorn qsot.server.api_server:app --host 0.0.0.0 --port 8000 &

# 2. Start Streamlit Dashboard in foreground
echo "📊 Starting QSOT Dashboard on port 8501..."
streamlit run src/qsot/server/dashboard.py --server.port 8501 --server.address 0.0.0.0