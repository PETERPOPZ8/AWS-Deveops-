FROM python:3.12-slim

WORKDIR /app

ENV APP_HOST=0.0.0.0
ENV APP_PORT=5000
ENV DATABASE_PATH=/app/data/students.db

COPY app.py requirements.txt ./
COPY static ./static
COPY templates ./templates

RUN mkdir -p /app/data

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3).read()"

CMD ["python", "app.py"]
