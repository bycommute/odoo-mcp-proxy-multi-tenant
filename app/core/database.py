"""
Configuration de la base de données
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./odoo_mcp_proxy.db")

# Créer l'engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Créer la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

def get_db():
    """Dependency pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Créer toutes les tables"""
    from .models import Base
    Base.metadata.create_all(bind=engine)

def init_db():
    """Initialiser la base de données"""
    create_tables()
