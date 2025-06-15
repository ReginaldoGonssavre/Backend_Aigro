# Backend (FastAPI)
FROM python:3.11-slim AS backend
WORKDIR /app
COPY backend/ ./backend/
RUN pip install fastapi[all] sqlalchemy passlib[bcrypt] pydantic[dotenv] python-jose qiskit

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]