# Kontekst budowania: katalog główny repo (docker-compose: context: ..)
FROM node:22-alpine AS front
WORKDIR /front
COPY app/frontend/package.json app/frontend/package-lock.json* ./
RUN npm install
COPY app/frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /srv/repo/app/backend
COPY app/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app/backend/ ./
COPY zakres-danych/ /srv/repo/zakres-danych/
COPY dane/wynik/ /srv/repo/dane/wynik/
COPY --from=front /front/dist /srv/repo/app/frontend/dist
ENV REPO_DIR=/srv/repo STATIC_DIR=/srv/repo/app/frontend/dist
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
