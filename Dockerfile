# Build the browser bundle once, then serve it and the FastAPI API from one container.
FROM node:20-slim AS frontend-build
WORKDIR /frontend
# Tailwind is a build-time dependency. Keep it available even if Render supplies NODE_ENV.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --include=dev
COPY frontend/ ./
ENV NODE_ENV=production
RUN npm run build

FROM python:3.10-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_ENV=production

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=frontend-build /frontend/out ./static

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
