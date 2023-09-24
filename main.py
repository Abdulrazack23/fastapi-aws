from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from mangum import Mangum;


app = FastAPI()
handler =Mangum(app)

DATABASE_URL = "sqlite:///./test.db"  


engine = create_engine(DATABASE_URL)

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)


Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ItemCreate(BaseModel):
    name: str
    description: str

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
@app.post("/items/", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    db_item = Item(**item.dict())
    with SessionLocal() as session:
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
    return db_item

@app.get("/items/", response_model=list[ItemResponse])
async def read_items(skip: int = 0, limit: int = 10):
    with SessionLocal() as session:
        items = session.query(Item).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=ItemResponse)
async def read_item(item_id: int):
    with SessionLocal() as session:
        item = session.query(Item).filter(Item.id == item_id).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
    return item
