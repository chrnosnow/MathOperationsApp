#  Base image with Python 3.12
FROM python:3.12

#  Set the working directory in the container
WORKDIR /app

# Install OS dependencies, including netcat (the watcher of ports)
RUN apt-get update && apt-get install -y build-essential netcat-openbsd dos2unix

# Copy all source files into the container
COPY . /app

# Add wait-for-kafka script
COPY wait-for-kafka.sh /app/wait-for-kafka.sh
# RUN chmod +x /app/wait-for-kafka.sh
RUN dos2unix /app/wait-for-kafka.sh \
    && chmod +x /app/wait-for-kafka.sh \
    && ls -l /app \
    && head -n1 /app/wait-for-kafka.sh

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8080

# Start the FastAPI app with Uvicorn
CMD ["/app/wait-for-kafka.sh", "kafka:9092", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]