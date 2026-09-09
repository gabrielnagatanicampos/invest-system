from hashlib import sha512
import uuid 
import database
import hmac

def generate_hash(password:str, salt = None):
    if salt is None:
        salt = uuid.uuid4().hex
    password_hash = sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    
    return password_hash, salt

def check_password(password:str, password_hash_bd: str, salt_bd: str):
   check_hash, salt = generate_hash(password, salt_bd) 
   
   return hmac.compare_digest(check_hash, password_hash_bd)

   
   
def login(username: str, password: str) -> bool:
    
    user = database.search_user(username)
    if user is None:
        return False
    
    password_hash_bd = user['password_hash']
    salt_bd = user ['salt']

    return check_password(password, password_hash_bd, salt_bd)



def register_user(username:str, password:str ):
    
    password_hash, salt = generate_hash(password)
    
    database.insert_user(username, password_hash, salt)




    

