"""
AigroQuantumSaaS - Backend principal (FastAPI)
"""
import sys, logging, jwt
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, BaseSettings, constr
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.hash import bcrypt
from uuid import uuid4

# Configuração
class Settings(BaseSettings):
    SECRET_KEY: str = "changeme"
    DB_URI: str = "sqlite:///./app.db"
    JWT_EXPIRE_MINUTES: int = 30
    LOG_LEVEL: str = "INFO"
    IBM_QISKIT_API_TOKEN: str = ""
    ALLOW_ORIGINS: str = "*"
    class Config:
        env_file = ".env"
settings = Settings()
logging.basicConfig(stream=sys.stdout, level=settings.LOG_LEVEL, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("aigroquantumsaas")

# Banco de dados e modelos
Base = declarative_base()
engine = create_engine(settings.DB_URI, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)
class QuantumJob(Base):
    __tablename__ = "quantum_jobs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    prompt = Column(Text)
    backend = Column(String(64))
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
Base.metadata.create_all(bind=engine)

# Segurança e autenticação
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
def hash_password(password: str) -> str:
    return bcrypt.hash(password)
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.verify(password, hashed)
def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception as ex:
        logger.warning(f"Token decode failed: {ex}")
        return None
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = decode_access_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido")
    return user

# App
app = FastAPI(title="AigroQuantumSaaS Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    id = str(uuid4())
    logger.info(f"REQUEST {id} - {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"RESPONSE {id} - status: {response.status_code}")
        return response
    except Exception as ex:
        logger.error(f"ERROR {id} - {ex}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)

# Modelos Pydantic
class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=30, regex="^[a-zA-Z0-9_.-]+$")
    password: constr(min_length=6, max_length=64)
class UserLogin(BaseModel):
    username: str
    password: str
class TokenResponse(BaseModel):
    access_token: str
class IARequest(BaseModel):
    module: str
    prompt: str
class QuantumJobResponse(BaseModel):
    id: int
    prompt: str
    backend: str
    result: str
    created_at: datetime

# Rotas
@app.post("/api/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=409, detail="Usuário já existe")
    user = User(username=data.username, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    logger.info(f"Novo usuário registrado: {data.username}")
    return {"msg": "Usuário criado"}
@app.post("/api/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    token = create_access_token(user.username)
    logger.info(f"Usuário logado: {data.username}")
    return TokenResponse(access_token=token)
def run_quantum_demo(prompt: str):
    try:
        from qiskit import QuantumCircuit, Aer, execute
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()
        backend = Aer.get_backend("aer_simulator")
        job = execute(qc, backend, shots=1024)
        result = job.result()
        counts = result.get_counts()
        return {"prompt": prompt, "backend": "aer_simulator", "counts": counts}
    except ImportError:
        return {"error": "Qiskit não instalado"}
    except Exception as ex:
        logger.error(f"Erro Quantum: {ex}")
        return {"error": str(ex)}
@app.post("/api/ia")
def ia_endpoint(req: IARequest, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.module.lower() == "quantum":
        result = run_quantum_demo(req.prompt)
        job = QuantumJob(user_id=user.id, prompt=req.prompt, backend=result.get("backend", "simulator"), result=str(result))
        db.add(job)
        db.commit()
        logger.info(f"Quantum job registrado: {job.id} para usuário {user.username}")
        return {"result": result}
    return {"result": f"Módulo {req.module} não implementado"}
@app.get("/api/users/me")
def get_me(user=Depends(get_current_user)):
    return {"username": user.username, "created_at": user.created_at, "is_admin": user.is_admin}
@app.get("/api/quantum/jobs", response_model=List[QuantumJobResponse])
def get_quantum_jobs(user=Depends(get_current_user), db: Session = Depends(get_db)):
    jobs = db.query(QuantumJob).filter(QuantumJob.user_id == user.id).order_by(QuantumJob.created_at.desc()).all()
    return [QuantumJobResponse(id=j.id, prompt=j.prompt, backend=j.backend, result=j.result, created_at=j.created_at) for j in jobs]
@app.get("/health")
def health():
    return {"status": "ok"}
@app.get("/", include_in_schema=False)
def root():
    return {"service": "AigroQuantumSaaS", "docs": "/docs", "health": "/health"}

def create_demo_admin():
    db = SessionLocal()
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(username="admin", password_hash=hash_password("admin123"), is_admin=True)
        db.add(admin)
        db.commit()
        logger.info("Usuário admin criado (senha: admin123)")
    db.close()
create_demo_admin()