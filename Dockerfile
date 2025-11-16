# Start with a base that has Python
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Flask port and run the app. Frontend assets are built by the
# separate `vite` service defined in docker-compose; the built files
# are placed under app/static/dist and served by Flask's static route.
EXPOSE 5000
CMD ["python", "run.py"]