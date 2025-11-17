# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# --- Node.js & Tailwind Setup ---
RUN apt-get update && \
    apt-get install -y curl gpg && \
    curl -sL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs build-essential && \
    # Clean up apt caches
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# --- Python Dependencies ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Node.js Dependencies (including concurrently) ---
COPY package.json package-lock.json* ./
COPY tailwind.config.js .
RUN mkdir -p /app/app/static/css
COPY app/static/css/input.css ./app/static/css/input.css
# Install deps and fix browserslist warning
RUN npm install && npx update-browserslist-db@latest

# --- Application Code ---
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Set the new default command
CMD ["npm", "run", "dev"]
