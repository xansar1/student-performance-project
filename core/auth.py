import hashlib

USERS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "college": hashlib.sha256("college123".encode()).hexdigest()
}

def check_login(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return USERS.get(username) == hashed
