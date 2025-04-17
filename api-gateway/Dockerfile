FROM python:3.11-slim

# Set environment variables

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY main.py .

# EXPOSE port
EXPOSE 5000

#Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]