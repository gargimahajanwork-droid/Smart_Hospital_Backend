from sqlalchemy import Column, Integer, String

# import base class
from database import Base

class Patient(Base):

    __tablename__ = "hospital_user"

    # index=true , can easily access the id 

    id = Column(Integer, primary_key=True , index=True)

    username = Column(String ,unique = True, nullable = False)

    password = Column(String , nullable = False)

    role = Column(String , nullable = False)

    patient_name = Column(String , nullable = False)

    age = Column(Integer)

    gender = Column(String)

    blood_group = Column(String)

    mobile = Column(String)
    
    email = Column(String)

