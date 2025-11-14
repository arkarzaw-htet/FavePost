from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.ext.mutable import MutableList  # ✅ ADD THIS
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

#Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    contents = Column(MutableList.as_mutable(JSON), default=list)  # ✅ FIXED HERE

Base.metadata.create_all(bind=engine)

# Pydantic schemas
class UserIn(BaseModel):
    username: str
    password: str

class UserUp(BaseModel):
    username: str
    post: str
    
class UserAuth(BaseModel):
    username: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.post("/register")
def register(user: UserIn, db: Session = Depends(get_db)):
    db_user = User(username=user.username, password=user.password, contents=[])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": f"User {db_user.username} created!"}

@app.post("/login")
def login(user: UserIn, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        return {"code": "Username not found"}
    if user.password != db_user.password:
        return {"code": "Wrong Password"}
    else:
        return {"contents": db_user.contents}

@app.post("/upload")
def send(user: UserUp, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        return {"code": "Username not found"}

    if db_user.contents is None:
        db_user.contents = []
    db_user.contents.append(user.post)
    db.commit()
    
    db.refresh(db_user)

@app.delete("/")
def send(user: UserAuth, db: Session = Depends(get_db)): # 👈 CHANGED UserUp to UserAuth
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        return {"code": "Username not found"}

    db_user.contents.clear()   
    db.commit()

    return {"message": "deleted"}