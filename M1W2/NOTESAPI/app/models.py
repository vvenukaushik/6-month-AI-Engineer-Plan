from database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, func
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    hashed_password = Column(String(100), nullable=False, index=True, unique=True)
    created_at = Column(DateTime, server_default=func.now())

class Notes(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    tags_str = Column(String(100), default="")
    owner_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


    @property
    def tags(self) -> list[str]:
        if not self.tags_str:
            return []
        return [t.strip() for t in self.tags_str.split(",") if t.strip()]
    
