from sqlalchemy import create_engine
# to establish a connection

# to create database sessions 
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import declarative_base 
# import declarative base to create models


DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost/hospital_db_new"


# create database engine 
engine = create_engine(DATABASE_URL)

# create sessions 
SessionLocal = sessionmaker(bind=engine)

# create base class
Base = declarative_base()

# dependency function 
def get_db():
    
    db =SessionLocal()

    try:

       yield db 
    #    use database session 

    finally:

        db.close()

        
