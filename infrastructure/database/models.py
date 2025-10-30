from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, BigInteger, JSON, TIMESTAMP, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    users = relationship("User", back_populates="role", cascade="all, delete", passive_deletes=True)
    role_commands = relationship("RoleCommand", back_populates="role", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    full_name = Column(String(255))
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    logs = relationship("ActionLog", back_populates="user")

class Command(Base):
    __tablename__ = "commands"

    id = Column(Integer, primary_key=True)
    command_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    role_commands = relationship("RoleCommand", back_populates="command", cascade="all, delete-orphan")

class RoleCommand(Base):
    __tablename__ = "role_commands"
    __table_args__ = (UniqueConstraint("role_id", "command_id", name="uq_role_command"),)

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    command_id = Column(Integer, ForeignKey("commands.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    role = relationship("Role", back_populates="role_commands")
    command = relationship("Command", back_populates="role_commands")

class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_type = Column(String(100))
    command_name = Column(String(100))
    details = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="logs")
