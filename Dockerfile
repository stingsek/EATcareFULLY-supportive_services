
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app/ .

RUN mkdir -p /data && chmod 777 /data

ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV DATASET_PATH=/data/openfoodfacts_sample.pkl
ENV SIMILARITIES_PATH=/data/similarities.csv
ENV MODEL_CACHE_SIZE=75

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]