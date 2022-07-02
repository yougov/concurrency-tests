FROM ubuntu:22.10 as base
LABEL dockerfile_cached_at="2022-07-02 10:47 UTC"

# Common packages
RUN apt update && \
    apt install -y \
    build-essential \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    python3-pip \
    curl \
    telnet \
    htop \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app
RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD ["python"]
