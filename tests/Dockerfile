FROM debian:trixie-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pil \
        zbar-tools \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /tests
COPY test_qr.py .
ENTRYPOINT ["python3", "-m", "unittest", "-v", "test_qr"]
