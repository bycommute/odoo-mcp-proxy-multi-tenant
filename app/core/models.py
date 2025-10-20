"""
Modèles de données pour le proxy MCP multi-tenant
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """Modèle utilisateur pour stocker les configurations Odoo"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Configuration Odoo
    odoo_url = Column(String(255), nullable=False)
    odoo_db = Column(String(100), nullable=False)
    odoo_username = Column(String(100), nullable=False)
    odoo_password = Column(String(255), nullable=False)  # Chiffré
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Informations utilisateur (optionnel)
    user_name = Column(String(100), nullable=True)
    user_email = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<User(user_id='{self.user_id}', odoo_url='{self.odoo_url}')>"

class APIToken(Base):
    """Modèle pour gérer les tokens API"""
    
    __tablename__ = "api_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(String(36), nullable=False, index=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Informations d'usage
    last_used = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<APIToken(token='{self.token[:8]}...', user_id='{self.user_id}')>"
