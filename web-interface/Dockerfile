FROM node:18-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package.json ./
RUN npm install

# Install nodemon globally
RUN npm install -g nodemon

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8080

# Start the application with nodemon for hot-reload
CMD ["npm", "run", "dev"]
