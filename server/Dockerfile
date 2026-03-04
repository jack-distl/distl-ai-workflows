FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run sets the PORT environment variable
ENV PORT=8000

EXPOSE 8000

CMD ["python", "main.py"]
