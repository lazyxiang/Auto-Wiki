# Use a mirror for the base image
FROM docker.m.daocloud.io/node:20-alpine

# Set working directory
WORKDIR /app

# Change Alpine repositories to Aliyun mirror
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

# Copy package files
COPY package.json package-lock.json* ./ 

# Set NPM registry to Aliyun mirror and install dependencies
RUN npm config set registry https://registry.npmmirror.com && \
    npm install --legacy-peer-deps

# Copy the rest of the application
COPY . .

# Build the application (Next.js)
# Note: For development 'npm run dev' is used in CMD, but for production use 'npm run build'
# Since we are running in dev mode via docker-compose usually, we can keep it simple.
# If this Dockerfile is for prod, we should build.
# For this MVP context, let's assume we want to run in dev mode or build if needed.
# The original file had just "COPY . .", let's check if it had a build step.
# It didn't seem to have a RUN build step in the previous logs, but 'npm install' was there.
# We will keep it consistent with development usage.

EXPOSE 3000

CMD ["npm", "run", "dev"]