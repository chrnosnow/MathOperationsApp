#  Base image with Python 3.12
FROM python:3.12

#  Set the working directory in the container
WORKDIR /app

# Copy all source files into the container
COPY . /app

# Install OS dependencies (optional but useful)
RUN apt-get update && apt-get install -y build-essential

# Copy requirements file and install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8080

# 🌟 Start the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "localhost", "--port", "8080"]