import hashlib

STUDENT_USERS = {
    "aarav": hashlib.sha256("student123".encode()).hexdigest(),
    "meera": hashlib.sha256("student123".encode()).hexdigest()
}


def student_login(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return STUDENT_USERS.get(username) == hashed
