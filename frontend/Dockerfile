# Frontend Dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build arguments for environment variables
ARG REACT_APP_API_URL
ARG REACT_APP_AI_SERVICE_URL

ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_AI_SERVICE_URL=$REACT_APP_AI_SERVICE_URL

# Build the app
RUN npm run build

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start the app
CMD ["npm", "start"]