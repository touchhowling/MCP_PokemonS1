# Start from a lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency list first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code into the container
COPY src ./src

# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Run the server when the container starts
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
