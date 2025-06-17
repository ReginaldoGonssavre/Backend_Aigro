# Frontend (React)
FROM node:18-alpine as frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build
EXPOSE 5173
CMD ["npm", "start"]