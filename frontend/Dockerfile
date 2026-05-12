FROM node:20-slim

WORKDIR /app

# Install dependencies first for caching
COPY package*.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Ensure .next directory exists and has correct permissions
RUN mkdir -p .next && chown -R node:node .next

# Set environment variables
ENV NEXT_PUBLIC_API_URL=http://api:8000/api/v1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

EXPOSE 3000

# Start in development mode with no-turbo as it is more stable in Docker environments
CMD ["npm", "run", "dev"]
