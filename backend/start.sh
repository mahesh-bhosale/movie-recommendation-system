#!/bin/bash

# Create necessary directories
mkdir -p app/ml_model

# Install dependencies
pip install -r requirements.txt

# Download model files
python -c "from app.download_models import download_models; download_models()"

# Run database migrations
alembic upgrade head

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port $PORT 