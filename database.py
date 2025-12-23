from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import Config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    grade_level = Column(String)  # SD, SMP, SMA
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    reflections = relationship("Reflection", back_populates="user", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")

class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    subject = Column(String, nullable=False)
    grade_level = Column(String, nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    ai_provider = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")

class Reflection(Base):
    __tablename__ = 'reflections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    subject = Column(String, nullable=False)
    reflection_text = Column(Text, nullable=False)
    correction = Column(Text)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reflections")

class Exam(Base):
    __tablename__ = 'exams'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    subject = Column(String, nullable=False)
    exam_data = Column(Text, nullable=False)  # JSON string of questions
    answers = Column(Text)  # JSON string of answers
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="exams")

class Reminder(Base):
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    email = Column(String, nullable=False)
    reminder_time = Column(String)  # e.g., "08:00"
    is_active = Column(Boolean, default=True)
    otp_code = Column(String)
    otp_expiry = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reminders")

class Cache(Base):
    __tablename__ = 'cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_hash = Column(String, unique=True, nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    subject = Column(String)
    grade_level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session()
    
    def add_user(self, user_data):
        session = self.get_session()
        try:
            user = User(**user_data)
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_user_by_email(self, email):
        session = self.get_session()
        try:
            return session.query(User).filter_by(email=email).first()
        finally:
            session.close()
    
    def get_user_by_id(self, user_id):
        session = self.get_session()
        try:
            return session.query(User).filter_by(id=user_id).first()
        finally:
            session.close()
    
    def update_user_grade(self, user_id, grade_level):
        session = self.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.grade_level = grade_level
                session.commit()
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_chat(self, chat_data):
        session = self.get_session()
        try:
            chat = ChatSession(**chat_data)
            session.add(chat)
            session.commit()
            return chat.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_reflection(self, reflection_data):
        session = self.get_session()
        try:
            reflection = Reflection(**reflection_data)
            session.add(reflection)
            session.commit()
            return reflection.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_exam(self, exam_data):
        session = self.get_session()
        try:
            exam = Exam(**exam_data)
            session.add(exam)
            session.commit()
            return exam.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_user_chats(self, user_id, subject=None):
        session = self.get_session()
        try:
            query = session.query(ChatSession).filter_by(user_id=user_id)
            if subject:
                query = query.filter_by(subject=subject)
            return query.order_by(ChatSession.created_at.desc()).all()
        finally:
            session.close()
    
    def get_cache(self, query_hash):
        session = self.get_session()
        try:
            cache = session.query(Cache).filter_by(query_hash=query_hash).first()
            if cache and cache.expires_at and cache.expires_at > datetime.utcnow():
                return cache.response
            return None
        finally:
            session.close()
    
    def set_cache(self, query_hash, query, response, subject=None, grade_level=None):
        session = self.get_session()
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=Config.CACHE_TTL)
            cache = Cache(
                query_hash=query_hash,
                query=query,
                response=response,
                subject=subject,
                grade_level=grade_level,
                expires_at=expires_at
            )
            session.add(cache)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
