from pydantic import BaseModel 

class RegistrationSchema(BaseModel):

    username : str 

    password: str 

    role: str 

    patient_name : str 

    age : int 

    gender : str 

    blood_group : str 

    mobile: str 


    email: str 

class LoginSchema(BaseModel):

    username : str 
    password : str 


# as per day 2 
# profile update schema 
class UpdateProfileSchema(BaseModel):

    patient_name : str 
    age: str
    gender : str 
    blood_group : str 
    mobile :str 
    email:str  
