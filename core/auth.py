import hashlib


# ---------------- DEMO USERS ----------------
# For Phase 4 this is okay.
# In Phase 5 we will replace this with DB users.
USERS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "college": hashlib.sha256("college123".encode()).hexdigest()
}


# ---------------- HASH HELPER ----------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------- LOGIN CHECK ----------------
def check_login(username: str, password: str) -> bool:
    hashed_password = hash_password(password)
    return USERS.get(username) == hashed_password
