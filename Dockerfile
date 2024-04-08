# Use the official Python image as base
FROM python:3.10

# Set environment variables
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

# Set working directory
WORKDIR /app

# Copy the application code
COPY ./src /app

# Install dependencies
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Command to run FastAPI using Uvicorn
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]