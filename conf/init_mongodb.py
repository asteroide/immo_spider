import getpass
import hashlib
from pymongo import MongoClient

spider_db = MongoClient().spider

admin_present = False
for user in spider_db.auth.find():
    if user["username"] == "admin":
        admin_present = True
        break

if not admin_present:
    password1 = getpass.getpass("Give a password for the admin user: ")
    password2 = getpass.getpass("Give the password again: ")
    if password1 == password2:
        user = {
            'username': "admin",
            'password': hashlib.sha256(password1.encode("utf-8")).hexdigest(),
            'role': ["admin"],
        }
        spider_db.auth.insert_one(user)
        print("Add 'admin' user with password supplied.")
    else:
        print("Passwords not corresponding...")
else:
    print("'admin' user already created.")
