import hashlib

PARENT_USERS = {
    "aarav_parent": hashlib.sha256("parent123".encode()).hexdigest(),
    "meera_parent": hashlib.sha256("parent123".encode()).hexdigest(),
}


def parent_login(username, password):
    username = username.strip().lower()
    password = password.strip()

    hashed = hashlib.sha256(password.encode()).hexdigest()

    return PARENT_USERS.get(username) == hashed
