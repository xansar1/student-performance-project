import hashlib

USERS = {
    "superadmin": {
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "SUPER_ADMIN",
        "college": "ALL"
    },
    "mg_admin": {
        "password": hashlib.sha256("mg123".encode()).hexdigest(),
        "role": "COLLEGE_ADMIN",
        "college": "MG University"
    },
    "ktu_hod": {
        "password": hashlib.sha256("ktu123".encode()).hexdigest(),
        "role": "HOD",
        "college": "KTU"
    }
}


def tenant_login(username, password):
    user = USERS.get(username)

    if not user:
        return None

    hashed = hashlib.sha256(password.encode()).hexdigest()

    if hashed == user["password"]:
        return {
            "username": username,
            "role": user["role"],
            "college": user["college"]
        }

    return None
