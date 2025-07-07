#!/bin/bash

export $(grep -v '^#' .env | xargs)
uvicorn deploy.api:app --host 0.0.0.0 --port 8000 --reload
