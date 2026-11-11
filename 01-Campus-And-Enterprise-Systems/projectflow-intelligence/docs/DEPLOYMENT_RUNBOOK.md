# Production Deployment Runbook

## Deployment Prerequisites
- Ubuntu 22.04 LTS or Amazon Linux 2023 instance with Docker and Docker Compose
- Supabase Project or Managed PostgreSQL 15+ instance
- Domain name with SSL certificates (Let's Encrypt / Cloudflare)

---

## 1. Environment Configuration
Create `/etc/projectflow/.env`:
```bash
SUPABASE_DB_URL=jdbc:postgresql://db.<REF>.supabase.co:5432/postgres?sslmode=require
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=<SECURE_PASSWORD>
JWT_SECRET=<32_BYTE_BASE64_SECRET>
CORS_ALLOWED_ORIGINS=https://app.yourdomain.com
```

---

## 2. Dockerized Backend Execution
```dockerfile
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY backend/build/libs/backend-2.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-Xmx1024m", "-jar", "app.jar"]
```

Run container:
```bash
docker run -d --name projectflow-backend -p 8080:8080 --env-file /etc/projectflow/.env projectflow-backend:2.0.0
```

---

## 3. Web Admin Panel Hosting
Build static bundle:
```bash
cd admin-panel
npm run build
```
Deploy contents of `admin-panel/dist` to Nginx, AWS S3 + CloudFront, or Vercel.
Configure Nginx reverse proxy for `/api/v1` to point to the backend at `http://localhost:8080/api/v1`.
