# Stage 1: Download/prepare dataset
FROM python:3.10-slim as dataset
WORKDIR /data

# copy dataset
COPY data/openfoodfacts_sample.pkl .
COPY data/similarities.csv .
COPY data/similarity_matrix.csv .

# Stage 2: Final image
FROM python:3.10-slim

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY ./app ./app

# create data volume
VOLUME ["/data"]

# copy dataset from previous stage
COPY --from=dataset /data/openfoodfacts_sample.pkl data/

ENV PYTHONPATH="/app:${PYTHONPATH}"
# environment variables
ENV DATASET_PATH=/data/openfoodfacts.pkl
ENV SIMILARITIES_PATH=/data/similarities.csv
ENV MODEL_CACHE_SIZE=75

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]