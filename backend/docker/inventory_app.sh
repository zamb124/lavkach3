#!/bin/bash

#alembic upgrade head


gunicorn app.inventory.server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8002