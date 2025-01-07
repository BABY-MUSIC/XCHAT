FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port
EXPOSE 8000

# Set the command to run the start script
CMD ["bash", "start.sh"]
