# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the app
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config for SPA routing with proper static file handling
RUN cat > /etc/nginx/conf.d/default.conf << 'EOF'
server {
    listen 8080;
    root /usr/share/nginx/html;
    index index.html;

    # Serve robots.txt with correct content type
    location = /robots.txt {
        add_header Content-Type text/plain;
        try_files $uri =404;
    }

    # Serve sitemap.xml with correct content type
    location = /sitemap.xml {
        add_header Content-Type application/xml;
        try_files $uri =404;
    }

    # Serve static assets with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # SPA fallback - serve index.html for all other routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
EOF

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
