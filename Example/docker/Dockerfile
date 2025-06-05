FROM python:3.9-slim

WORKDIR /app

# Install the dependencies required for compilation
RUN apt-get update && apt-get install -y gcc build-essential

# Copy full code
COPY src /app

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Command that starts the process
CMD ["faust", "-A", "stream_processor", "worker", "-l", "info"]
