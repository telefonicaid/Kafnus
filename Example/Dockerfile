FROM python:3.9-slim

WORKDIR /app

# Install the dependencies required for compilation
RUN apt-get update && apt-get install -y gcc build-essential

# Copy requirements and code
COPY requirements.txt .
COPY stream_processor.py .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Command that starts the process
CMD ["faust", "-A", "stream_processor", "worker", "-l", "info"]
