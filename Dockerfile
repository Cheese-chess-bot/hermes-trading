FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy all files from your space into the container
COPY . .

# Install dependencies directly
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the state directory is copied
COPY state/ /app/state/

# Tell Hugging Face we are using the standard web port
EXPOSE 7860

# Start the application
CMD ["python", "app.py"]
