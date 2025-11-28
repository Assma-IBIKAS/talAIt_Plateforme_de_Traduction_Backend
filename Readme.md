# 🚀 TalAIt Translation Platform - Backend API

## 📋 Description

API Backend sécurisée développée en **FastAPI** pour la plateforme de traduction de TalAIt. Cette API permet aux équipes de traduire rapidement des textes entre le français et l'anglais en utilisant les modèles Hugging Face, avec une authentification JWT robuste.

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│   (Next.js)     │
└────────┬────────┘
         │ HTTP + JWT
         ▼
┌─────────────────┐
│   FastAPI       │
│   Backend       │
└────┬────────┬───┘
     │        │
     │        └──────────────┐
     ▼                       ▼
┌─────────────┐    ┌──────────────────┐
│ PostgreSQL  │    │  Hugging Face    │
│   Database  │    │  Inference API   │
└─────────────┘    └──────────────────┘
```

## 🛠️ Technologies Utilisées

- **Framework**: FastAPI 
- **Base de données**: PostgreSQL 18
- **ORM**: SQLAlchemy 
- **Authentification**: JWT (python-jose)
- **Sécurité**: hashlib pour le hashing des mots de passe
- **API IA**: Hugging Face Inference API
- **Validation**: Pydantic
- **Documentation**: Swagger UI 

## 📦 Prérequis

- Python 3.11+
- PostgreSQL 15+
- Token Hugging Face API (gratuit)
- Docker & Docker Compose (optionnel)

## ⚙️ Installation

### 1. Cloner le repository

```bash
git clone https://github.com/Assma-IBIKAS/talAIt_Plateforme_de_Traduction_Backend.git
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration des variables d'environnement

Créer un fichier `.env` à la racine du dossier backend :

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/talAIt_db

# JWT Configuration
SECRET_KEY=votre_secret_key_super_securisee_changez_la
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Hugging Face API
HF_API_TOKEN=votre_token_hugging_face
HF_API_URL=https://api-inference.huggingface.co/models

# Models
MODEL_FR_EN=Helsinki-NLP/opus-mt-fr-en
MODEL_EN_FR=Helsinki-NLP/opus-mt-en-fr

# Server
HOST=0.0.0.0
PORT=8000
```

### 5. Initialiser la base de données

```bash
# Créer la base de données PostgreSQL
createdb talAIt_db

# Les tables seront créées automatiquement au démarrage
```

## 🚀 Lancement

### Mode développement

```bash
uvicorn main:app --reload 
```

### Mode production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Avec Docker

```bash
# Build l'image
docker build -t talAIt-backend .

# Lancer le conteneur
docker run -p 8000:8000 --env-file .env talait-backend
```

### Avec Docker Compose (recommandé)

```bash
# Depuis la racine du projet
docker-compose up -d
```

## 📚 Documentation API

Une fois l'application lancée, la documentation interactive est disponible sur :

- **Swagger UI**: http://localhost:8000/docs

## 🔐 Endpoints

### Authentification

#### POST `/register`
Création d'un nouveau compte utilisateur.

**Request Body:**
```json
{
  "username": "user@talait.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "user@talait.com"
}
```

---

#### POST `/login`
Connexion et obtention d'un token JWT.

**Request Body (form-data):**
```
username: user@talait.com
password: SecurePass123!
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Traduction (🔒 Protégé)

#### POST `/translate`
Traduit un texte entre français et anglais.

**Headers:**
```
Authorization: Bearer <votre_token_jwt>
```

**Request Body:**
```json
{
  "text": "Bonjour, comment allez-vous ?",
  "direction": "fr-en"
}
```

**Response:**
```json
{
  "original_text": "Bonjour, comment allez-vous ?",
  "translated_text": "Hello, how are you?",
  "direction": "fr-en"
```

**Directions supportées:**
- `fr-en`: Français → Anglais
- `en-fr`: Anglais → Français

## 🔧 Structure du Projet

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Point d'entrée FastAPI
│   ├── database.py          # Connexion DB
│   ├── models.py            # Modèles SQLAlchemy
│   ├── schemas.py           # Schémas Pydantic
│   ├── huggingface.py   # Service Hugging Face
├── tests/
│   ├── test_unitaire.py
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## 🧪 Tests

### Lancer les tests unitaires

```bash
# Tous les tests
pytest
```

## 🛡️ Sécurité

### Workflow d'authentification

```
1. User Register/Login
        ↓
2. Backend valide credentials
        ↓
3. Backend génère JWT (expire après 30min)
        ↓
4. Frontend stocke le token
        ↓
5. Frontend envoie token dans Authorization header
        ↓
6. Backend vérifie et décode le JWT
        ↓
7. Si valide → accès endpoint protégé
   Si invalide → 401 Unauthorized
```

### Bonnes pratiques implémentées

✅ Passwords hashés avec hashlib  
✅ JWT avec expiration (30 minutes)  
✅ CORS configuré pour le frontend uniquement  
✅ Rate limiting sur les endpoints sensibles  
✅ Validation stricte des inputs (Pydantic)  
✅ Gestion des erreurs centralisée  
✅ Variables sensibles dans .env (jamais commitées)  

## ⚠️ Gestion des Erreurs

### Codes HTTP retournés

| Code | Description |
|------|-------------|
| 200 | Succès |
| 201 | Créé (register) |
| 400 | Bad Request (données invalides) |
| 401 | Unauthorized (JWT manquant/invalide) |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |
| 503 | Service Unavailable (Hugging Face down) |


## 🌐 Intégration Hugging Face

### Modèles utilisés

1. **FR → EN**: `Helsinki-NLP/opus-mt-fr-en`
2. **EN → FR**: `Helsinki-NLP/opus-mt-en-fr`

### Limitations

- **Rate Limit**: 1000 requêtes/jour (compte gratuit)
- **Timeout**: 30 secondes par requête
- **Taille max**: 1000 caractères par traduction
- **Disponibilité**: 99% (cold start possible)

### Gestion des erreurs Hugging Face

```python
# Timeout après 30s
# Retry automatique (3 tentatives)
# Fallback si modèle indisponible
# Log détaillé des erreurs
```

## 🐳 Docker

### Build l'image

```bash
docker build -t talait-backend:latest .
```


## 🔄 Workflow Complet

```
1. Utilisateur s'inscrit → POST /register
2. Utilisateur se connecte → POST /login → reçoit JWT
3. Frontend stocke le JWT (localStorage/cookie)
4. Utilisateur demande une traduction → POST /translate
5. Backend vérifie le JWT
6. Backend appelle Hugging Face API
7. Backend retourne la traduction
8. Frontend affiche le résultat
```
---

**Développé avec ❤️ par l'équipe TalAIt Tech**