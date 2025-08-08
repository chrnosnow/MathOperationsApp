#  Base image with Python 3.12
FROM python:3.12

#  Set the working directory in the container
WORKDIR /app

# Copy all source files into the container
COPY . /app

# Install OS dependencies (optional but useful)
RUN apt-get update && apt-get install -y build-essential

# Install OS dependencies, including netcat (the watcher of ports)
RUN apt-get update && apt-get install -y build-essential netcat-openbsd

# Copy requirements file and install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add wait-for-kafka script
COPY wait-for-kafka.sh /app/wait-for-kafka.sh
RUN chmod +x /app/wait-for-kafka.sh

# Expose FastAPI port
EXPOSE 8080

# Start the FastAPI app with Uvicorn
CMD ["/app/wait-for-kafka.sh", "kafka:9092", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]