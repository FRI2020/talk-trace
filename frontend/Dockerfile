FROM python:3.9-slim
WORKDIR /app

COPY . ./
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip

RUN pip install -r requirements.txt



EXPOSE 9090

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=9090", "--server.address=0.0.0.0"]
