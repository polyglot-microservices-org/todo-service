FROM python:3.9-slim

WORKDIR /usr/src/app

# Install dependencies first (caching advantage)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

EXPOSE 5001

# Single entrypoint
ENTRYPOINT ["python", "main.py"]

