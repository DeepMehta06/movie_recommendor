#!/bin/bash

echo "🚀 Starting Movie Recommender System..."
echo "📦 Python version: $(python --version)"
echo "💾 Memory available: $(free -h | grep Mem | awk '{print $7}')"
echo "📂 Current directory: $(pwd)"
echo "📋 Files present:"
ls -lh *.pkl

echo ""
echo "🔧 Starting Streamlit app..."
streamlit run app.py \
  --server.port=${PORT:-8501} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --browser.gatherUsageStats=false
