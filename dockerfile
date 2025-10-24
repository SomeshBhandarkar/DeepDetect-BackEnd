
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir torch==2.2.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app


RUN mkdir -p /app/models /app/uploads

EXPOSE 8000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

