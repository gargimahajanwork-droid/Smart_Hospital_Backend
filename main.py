from fastapi import FastAPI,Depends,HTTPException

from database import Base,engine,get_db

from sqlalchemy.orm import session

from schemas import RegistrationSchema,LoginSchema,UpdateProfileSchema

from models import Patient

from passlib.context import CryptContext
from jose import jwt 
from datetime import datetime , timedelta, timezone
# current date , time , time difference and utc time zone 

app = FastAPI()

Base.metadata.create_all(bind= engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = 'auto')

SECRET_KEY = "hospital_secret_key"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# create a fucntion to generate  a JWT access token 
def create_access_token(data: dict):

    # make a copy of the user data(payload)
    # create a copy so we can safely add the expiry time without changing the original data 
    to_encode = data.copy()

    # calculate the token expiry time 
    # current utc time +token expiry duration (e.g 30 minutes)

    expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)

#    add the  expiry tume to the payload 
# after this time, the token will no longer be valid 
    to_encode.update({"exp": expire})

    # generate the jwt token
    # the payload is digitally signed using the secret key and algorithm 
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token

@app.post("/register")

def register_user(user: RegistrationSchema, db: session= Depends(get_db)):
    existing_user = db.query(Patient).filter(Patient.username == user.username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="username already exist")
    
    hashed_password = pwd_context.hash(user.password)
    
    # create patient object 
    new_user = Patient(
          
               username = user.username, 

               password = hashed_password,

               role= user.role,

               patient_name = user.patient_name, 

               age = user.age,

               gender = user.gender, 

               blood_group = user.blood_group,

               mobile = user.mobile, 

               email = user.email)
    
    db.add(new_user)

    db.commit()
    db.refresh(new_user)

    return {"message":"user addedd successfully"}

# create endpoint for patient login 
@app.post("/login")
def login_user(user:LoginSchema, db :session = Depends(get_db)):
   
   existing_user = db.query(Patient).filter(Patient.username == user.username).first()

   if not existing_user:
       raise HTTPException(status_code=404, detail="user not found")
   
#    verify password
   if not pwd_context.verify(user.password, existing_user.password):
       
       raise HTTPException(status_code=401, detail="invalid password")
   
   payload = {"sub": existing_user.username, "role": existing_user.role}
#    create the payload containing the user's username and role and this information will be stored inisde the jwt token

# generate a jwt access token using the payload 
   access_token = create_access_token(payload)
# return the generated jwt token and specify the use this token in the authorisation header with the bearer prefix 
   return {"access_token": access_token, "token_type": "bearer"}
# this API verifies the user's login credentials , creates a jwt token containing the user's details and returns 
# the token for accessing protected apis which we will create later 

# as per day 2 
# jwterror which is used to catch invalid jwt tokens (wrong, expired, modified)
from jose import JWTError
# import bearer authentication reads the authorization header (authorization Bearer ejdi.....)
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
# http auth cred stores the token sent by the user 


# create bearer object , as it automatically extracts (Bearer eyhdi...)

security = HTTPBearer()

# function  to verify the jwt roken received in the authorization header 
def verify_token(credentials : HTTPAuthorizationCredentials = Depends(security)):
    # depends(security) automatically extracts the token from the request header , while 
    # credentails , stores the authorization header containing the bearer token 


    try:
    # try to validate the verify_token
        token = credentials.credentials
    #  extract only the jwt token from the authorisation header eg "bearer <token>" -> "token"

    # decode token 
        payload = jwt.decode(token , SECRET_KEY, algorithms=[ALGORITHM])
    # verify the token using the secret key and algorithm , if valid , extract the user information (payload)

    # Depends(security) automatically extracts the Authorization header.
    # It validates that it uses the Bearer scheme and stores the result
    # in the 'credentials' object, which contains:
    # credentials.scheme -> "Bearer"
    # credentials.credentials -> the actual JWT token

        return payload
# return the decoded user information stored inside the token 
   
    except JWTError:
        # exectue if th token is invalid , expired or modified

        raise HTTPException(status_code=401, detail="Invalid token")
        # return an unauthorised access error 
    # this function extracts the jwt token from the authorisation header , verifies it and returns the user information if the token is valid 

     
# creates protected api endpoint 
@app.get("/protected")
def protected_route(payload : dict = Depends(verify_token)):
    # it allows access only after the jwt token is successfully verified and payload contains the user 
    # information extracted from the token 

    # return response 
    return {"message": "Access Granted", "payload": payload}

# now go to postman and verify where it means your jwt token is valid , the user vivek123 is authenticated 
# has the role patient , and the token will expire at the specified time (exp).

# create endpoint for patient profile 
@app.get("/profile")

def get_profile(payload: dict = Depends(verify_token), db: session= Depends(get_db)):

    # extract the username stored inside the jwt 
    username = payload ["sub"]

    existing_user = db.query(Patient).filter(Patient.username==username).first()

    if not existing_user: 
        raise HTTPException(status_code=404, detail="User not found")
    
    # return reponse user details 
    return {

        "id" :existing_user.id,
        "username":existing_user.username,
        "role":existing_user.role,
        "patient_name":existing_user.patient_name,
        "age":existing_user.age,
        "gender":existing_user.gender,
        "blood_group":existing_user.blood_group,

        "mobile":existing_user.mobile,
        "email":existing_user.email

    }

# /protected only verifies the jwt token whereas /profile also needs the query the database
# so it requires db:session = Depends(get_db)
@app.put("/update_profile")

def update_profile(updated_user : UpdateProfileSchema, payload : dict= Depends(verify_token), db :session = Depends(get_db)):
    # extract the username stored inside the jwt 
    username = payload["sub"]

    existing_user = db.query(Patient).filter(Patient.username == username).first()

    if not existing_user: 
        raise HTTPException(status_code=404, detail="user not found")
    
    # update patient name 
    existing_user.patient_name = updated_user.patient_name,
    existing_user.age = updated_user.age,
    existing_user.gender = updated_user.gender,
    existing_user.blood_group = updated_user.blood_group,
    existing_user.mobile = updated_user.mobile,
    existing_user.email = updated_user.email,


    db.commit()
    db.refresh(existing_user)

    return {"message": "user updated successfully"}




# as per day 2 uploadidng a file 
# import uploadifle 

from fastapi import UploadFile
from fastapi import File
import os 

os.makedirs("uploads", exist_ok = True)
# create the uploads folder if it doesnt exist and do nothing if the folder already exists 


# create endpoint for uploading medical report 
@app.post("/upload_report")
def upload_report(file : UploadFile = File(...), payload : dict = Depends(verify_token)):
    # here the uploadFile specifies what kind of data am i expecting (ANS is a file, and it can be of anytype)
    #  File(...) specifies, is the file required (ans is yes, make it mandatory)
    # verify token () checks the user's JWT token before allowing to upload the file

    file_path = f"uploads/{file.filename}"
    # create the location where u want to save the uploaded file 
    # now , suppose the uploaded file is blood_report.pdf then file_path becomes uploads/blood_report.pdf

    with open(file_path, "wb") as saved_file:

        # when the user uploads a file , it is in fastapi memory(ram)
        # then write binary coverts it into 0 1 form and python reads it and then passes it into the blank file 
        # it creates a new blank file , copies the uploaded data from the fastapi memory into it
        # and saves it permanently in the uploads folder 
        saved_file.write(file.file.read())
    
    # extract username 
    username = payload["sub"]

    return {"message": "Medical Report Uploaded Successfully", "filename": file.filename, "uploaded.py":username}
    
# this api first verifies the user's JWT  token, thne uploads the mdeical report and saves it in the uploads folder 


