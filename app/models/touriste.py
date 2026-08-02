from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Touriste(Base):
    __tablename__ = "touriste"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
