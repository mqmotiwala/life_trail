from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    categories = relationship('Category', back_populates='user')
    activities = relationship('Activity', back_populates='user')
    activity_logs = relationship('ActivityLog', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='categories')
    activities = relationship('Activity', back_populates='category')

class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    category = relationship('Category', back_populates='activities')
    user = relationship('User', back_populates='activities')
    logs = relationship('ActivityLog', back_populates='activity')

class ActivityLog(Base):
    __tablename__ = 'activity_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, nullable=False)
    category_name = Column(String(255), nullable=False)
    activity_id = Column(Integer, ForeignKey('activities.id'))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    activity_name = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    activity = relationship('Activity', back_populates='logs')
    user = relationship('User', back_populates='activity_logs')