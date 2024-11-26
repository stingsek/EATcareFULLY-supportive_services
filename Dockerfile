# Stage 1: Download/prepare dataset
FROM python:3.11-slim as dataset
WORKDIR /data/processed

# copy dataset
COPY openfoodfacts.pkl .

# Stage 2: Final image
FROM python:3.11-slim
WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY ./app ./app

# create data volume
VOLUME ["/app/data/processed"]

# copy dataset from previous stage
COPY --from=dataset /data/processed/openfoodfacts.pkl /app/data/processed

# environment variables
ENV DATASET_PATH=/app/data/processed/openfoodfacts.pkl
ENV MODEL_CACHE_SIZE=75

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]