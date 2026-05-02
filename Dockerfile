FROM python:3.12-slim AS backend
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY backend /app/backend
WORKDIR /app/backend
ENV DATABASE_URL=sqlite:////app/data/assistant.db
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM node:22-alpine AS frontend-deps
WORKDIR /app
COPY frontend/package.json /app/package.json
RUN npm install

FROM node:22-alpine AS frontend-builder
WORKDIR /app
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
COPY --from=frontend-deps /app/node_modules ./node_modules
COPY frontend .
RUN npm run build

FROM node:22-alpine AS frontend
WORKDIR /app
ENV NODE_ENV=production
COPY --from=frontend-builder /app/.next/standalone ./
COPY --from=frontend-builder /app/.next/static ./.next/static
COPY --from=frontend-builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
