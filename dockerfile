# backend/Dockerfile
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy requirements first for caching
COPY requirements.txt .

# upgrade pip then install torch cpu wheel and other python deps
RUN pip install --upgrade pip

# Install CPU PyTorch wheel (uses official PyTorch CPU wheel index)
# (keeps torch separate to use the cpu wheel index)
RUN pip install --no-cache-dir torch==2.2.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Install the rest of requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app

# Create models and uploads dirs (if not present)
RUN mkdir -p /app/models /app/uploads

EXPOSE 8000

# default command: start uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
