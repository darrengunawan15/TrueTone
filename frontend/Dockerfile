FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY . .

# Expose port
EXPOSE 5173

# Start dev server (change to 'npm run build' + serve for production)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

