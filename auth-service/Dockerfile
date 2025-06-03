From python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /data

COPY . .
RUN chmod +x ./entrypoint.sh
EXPOSE 5003

ENTRYPOINT ["./entrypoint.sh"]