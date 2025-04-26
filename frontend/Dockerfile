# Use Node.js for the build step
FROM node:18 AS build

ENV VITE_API_URL=/api

# Log the API URL being used
RUN echo "Using API URL: /api"

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy app files and build Vue app
COPY . .
RUN npm run build

# Use Nginx for serving the built app
FROM nginx:latest

# Copy Vue build to Nginx
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose the web server port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
