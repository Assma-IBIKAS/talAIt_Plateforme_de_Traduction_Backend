import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from hugging_face import translate as hf_translate
import httpx
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from schemas import *

from db import get_db, Base, engine  
from models import User  


from dotenv import load_dotenv
load_dotenv()

from fastapi.middleware.cors import CORSMiddleware


# ---------- Config JWT ----------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ---------- Config HF ----------
HF_TOKEN = os.getenv("HF_TOKEN")  
HF_TIMEOUT = int(os.getenv("HF_TIMEOUT_SECONDS","60"))

# ---------- FastAPI app ----------
app = FastAPI(title="talAIt Platforme Translate")

# import des modèles / Base avant create_all
Base.metadata.create_all(bind=engine) 

origins = [
    "http://localhost:3000",   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Helpers for password & JWT ----------
def get_password_hash(password: str) -> str:
    # simple sha256 pour ton projet actuel 
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": subject}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

# OAuth2 dependency (reads Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide ou expiré")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
    return username

# ---------- Endpoints ----------

@app.get("/")
def root():
    return {"msg": "Hello talAIt Platforme Translate !!"}

@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    """Retourne tous les utilisateurs """
    users = db.query(User).all()
    # map vers dict sans password_hash
    return [{"id": u.id, "username": u.username} for u in users]

@app.post("/register", response_model=dict, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Créer un nouvel utilisateur"""
    # vérifier existence
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = get_password_hash(user_in.password)
    new_user = User(username=user_in.username, password_hash=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}

@app.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login - retourne JWT (utilise OAuth2PasswordRequestForm pour compatibilité)"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")

    token = create_access_token(subject=user.username)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/translate", response_model=TranslateResponse)
def translate_endpoint(
    req: TranslateRequest,
    username: str = Depends(get_current_username),
    token: str = Depends(oauth2_scheme),   # token JWT brut si tu veux le logger ou le passer
    request: Request = None,
):
    """Endpoint protégé : appelle Hugging Face (hf_translate) et retourne la traduction."""
    # validation d'entrée
    if not req.text or req.direction not in ("fr-en", "en-fr"):
        raise HTTPException(status_code=400, detail="Format d'entrée invalide (text & direction attendus).")

    # log simple
    # print(f"[translate] user={username} direction={req.direction} len_text={len(req.text)}")

    # appeler hugging_face (fonction synchrone)
    try:
        result = hf_translate(req.text, req.direction)
    except Exception as e:
        # protège contre toute exception non prévue dans hf_translate
        raise HTTPException(status_code=502, detail=f"Erreur interne lors de l'appel HF: {e}")

    # gérer erreurs renvoyées par HF
    if isinstance(result, dict) and result.get("error"):
        # renvoie le message d'erreur HF (502 Bad Gateway)
        raise HTTPException(status_code=502, detail=result.get("error"))

    # extraire la traduction attendue
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
        translation = result[0].get("translation_text") or result[0].get("generated_text")
        if translation:
            return {"translation": translation}

    # si format inattendu
    raise HTTPException(status_code=502, detail="Réponse Hugging Face inattendue")
