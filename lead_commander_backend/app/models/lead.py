"""
lead.py
-------
Defines the Lead model for database representation.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Lead(Base):
    """
    Skeleton SQLAlchemy model for a lead.
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    # Add more fields as needed

    def __repr__(self):
        return f"<Lead(name={self.name}, email={self.email})>"
