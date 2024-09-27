from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

DATABASE_URL = "postgresql://postgres:habiba@localhost/random"

engine = create_engine(DATABASE_URL, echo=True)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "hqwlkstuchponbcyeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9eyJzd"
ALGORITHM = "HS256"

app = FastAPI()

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_session():
    with Session(engine) as session:
        yield session

def create_access_token(data: dict, expire_delta: timedelta | None):
    to_encode = data.copy()
    expire_delta = datetime.utcnow() + (expire_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire_delta})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
  
    try:
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if user is None:
            raise credentials_exception
    return user

@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)

class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password: str
    creation_date: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with Orders

class Prediction(SQLModel, table=True):
    prediction_id:  Optional[int] = Field(default=None, primary_key=True)
    predicted_outcome: str
    username: str
    
    


@app.post("/user/")
def create_user(user: User, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User with the same username already exists")
    user.password = hash_password(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expire = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": form_data.username}, expire_delta=access_token_expire)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/prediction/")
def prediction(prediction : Prediction , session: Session = Depends(get_session), current_user : User = Depends(get_current_user)):
    prediction.username = current_user.username 
    session.add(prediction)
    session.commit()
    session.refresh(prediction)
    return prediction
