FROM python:3.9-slim
WORKDIR /app

COPY . ./
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*



COPY requirements.txt .
RUN pip install --upgrade pip

RUN pip install -r requirements.txt



EXPOSE 8080

CMD ["python", "app.py"]