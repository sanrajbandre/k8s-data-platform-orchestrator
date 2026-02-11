FROM python:3.12-slim
WORKDIR /app
COPY worker /app
RUN pip install --upgrade pip && pip install .
CMD ["celery", "-A", "app.celery_app", "worker", "-l", "INFO"]
