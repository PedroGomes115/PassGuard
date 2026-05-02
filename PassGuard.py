import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import base64
import getpass
import time
import tempfile
import atexit


# Banner

print("")

def banner():
    title = "PassGuard"
    author = "Made by: Pedro Gomes"
    width = max(len(title), len(author)) + 10  

    print("-" * width)
    print(title.center(width))
    print(author.center(width))
    print("-" * width)
    print("")

banner()



DB_FILE = "passwords.db.enc"  # Encrypted DB
KEY_FILE = "secret.key"
SALT_FILE = "salt.key"
MAX_ATTEMPTS = 5

# Secure temporary DB
TEMP_DB_FILE = tempfile.NamedTemporaryFile(delete=False)
TEMP_DB = TEMP_DB_FILE.name
TEMP_DB_FILE.close()
atexit.register(lambda: os.remove(TEMP_DB) if os.path.exists(TEMP_DB) else None)

# Key Derivation 
def derive_master_key(master_password, salt, pepper):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,
    )
    return base64.urlsafe_b64encode(kdf.derive((master_password + pepper).encode()))

# Key
def load_or_create_key():
    pepper = getpass.getpass("Enter a pepper (extra secret, can be random): ")

    if not os.path.exists(KEY_FILE) or not os.path.exists(SALT_FILE):
        print("=== First-time setup ===")
        master_password = getpass.getpass("Set a master password (any password is allowed): ")

        salt = os.urandom(16)
        with open(SALT_FILE, "wb") as f:
            f.write(salt)

        master_key = derive_master_key(master_password, salt, pepper)
        secret_key = Fernet.generate_key()
        encrypted_secret = Fernet(master_key).encrypt(secret_key)

        with open(KEY_FILE, "wb") as f:
            f.write(encrypted_secret)

        print("Setup complete!")
        return secret_key, master_password

    else:
        attempts = 0
        with open(SALT_FILE, "rb") as f:
            salt = f.read()
        with open(KEY_FILE, "rb") as f:
            encrypted_secret = f.read()

        while attempts < MAX_ATTEMPTS:
            master_password = getpass.getpass("Enter master password: ")
            pepper = getpass.getpass("Enter pepper: ")

            master_key = derive_master_key(master_password, salt, pepper)

            try:
                secret_key = Fernet(master_key).decrypt(encrypted_secret)
                return secret_key, master_password
            except:
                attempts += 1
                print("Incorrect password or pepper!")
                time.sleep(2)

        print("Too many failed attempts. Exiting.")
        exit()

# DB Encryption and Decryption 
def decrypt_db(secret_key):
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(TEMP_DB)
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS passwords (
                site TEXT,
                username TEXT,
                password TEXT,
                notes TEXT
            )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS general_notes (
                title TEXT,
                note TEXT
            )"""
        )
        conn.commit()
        conn.close()
        return

    with open(DB_FILE, "rb") as f:
        encrypted_data = f.read()
    fernet = Fernet(secret_key)
    decrypted_data = fernet.decrypt(encrypted_data)

    with open(TEMP_DB, "wb") as f:
        f.write(decrypted_data)

def encrypt_db(secret_key):
    with open(TEMP_DB, "rb") as f:
        data = f.read()
    fernet = Fernet(secret_key)
    encrypted_data = fernet.encrypt(data)
    with open(DB_FILE, "wb") as f:
        f.write(encrypted_data)
    os.remove(TEMP_DB)

# Database Connection 
def init_db():
    conn = sqlite3.connect(TEMP_DB)
    return conn

# Password CRUD Operations 
def add_password(conn, fernet):
    site = input("Site: ")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    notes = input("Notes (optional): ")

    encrypted = fernet.encrypt(password.encode())
    c = conn.cursor()
    c.execute(
        "INSERT INTO passwords (site, username, password, notes) VALUES (?, ?, ?, ?)",
        (site, username, encrypted, notes),
    )
    conn.commit()
    print("Password added!")

def view_passwords(conn, fernet):
    c = conn.cursor()
    c.execute("SELECT site, username, password, notes FROM passwords")
    rows = c.fetchall()
    if not rows:
        print("No passwords stored yet.")
        return
    for site, username, encrypted, notes in rows:
        password = fernet.decrypt(encrypted).decode()
        print(f"Site: {site}, Username: {username}, Password: {password}, Notes: {notes}")

def search_password(conn, fernet):
    print("Search by:\n1. Site\n2. Username\n3. Password")
    choice = input("Select option: ")
    term = input("Enter search term: ").lower()

    c = conn.cursor()
    c.execute("SELECT site, username, password, notes FROM passwords")
    rows = c.fetchall()
    found = False

    for site, username, encrypted, notes in rows:
        password = fernet.decrypt(encrypted).decode()
        if (choice == "1" and term in site.lower()) or \
           (choice == "2" and term in username.lower()) or \
           (choice == "3" and term in password.lower()):
            print(f"Site: {site}, Username: {username}, Password: {password}, Notes: {notes}")
            found = True

    if not found:
        print("No matching entry found.")

def edit_password(conn, fernet):
    site = input("Enter site to edit: ")
    c = conn.cursor()
    c.execute("SELECT site, username, password, notes FROM passwords WHERE site = ?", (site,))
    row = c.fetchone()
    if not row:
        print("Site not found.")
        return

    username, old_encrypted, notes = row[1], row[2], row[3]
    print(f"Current username: {username}")
    print(f"Current notes: {notes}")

    new_username = input("New username (leave empty to keep current): ")
    new_password = getpass.getpass("New password (leave empty to keep current): ")
    new_notes = input("New notes (leave empty to keep current): ")

    if new_username.strip() == "":
        new_username = username
    if new_password.strip() == "":
        encrypted_password = old_encrypted
    else:
        encrypted_password = fernet.encrypt(new_password.encode())
    if new_notes.strip() == "":
        new_notes = notes

    c.execute(
        "UPDATE passwords SET username = ?, password = ?, notes = ? WHERE site = ?",
        (new_username, encrypted_password, new_notes, site),
    )
    conn.commit()
    print("Password updated!")

def delete_password(conn):
    site = input("Enter site to delete: ")
    c = conn.cursor()
    c.execute("DELETE FROM passwords WHERE site = ?", (site,))
    if c.rowcount == 0:
        print("Site not found.")
    else:
        conn.commit()
        print("Password deleted!")

# General Notes CRUD Operations (Encrypted) 
def add_note(conn, fernet):
    title = input("Title of note: ")
    note = input("Note content: ")

    encrypted_note = fernet.encrypt(note.encode())
    c = conn.cursor()
    c.execute(
        "INSERT INTO general_notes (title, note) VALUES (?, ?)",
        (title, encrypted_note),
    )
    conn.commit()
    print("Note added!")

def view_notes(conn, fernet):
    c = conn.cursor()
    c.execute("SELECT title, note FROM general_notes")
    rows = c.fetchall()
    if not rows:
        print("No notes stored yet.")
        return
    for title, encrypted_note in rows:
        note = fernet.decrypt(encrypted_note).decode()
        print(f"Title: {title}\nNote: {note}\n---")

def edit_note(conn, fernet):
    title = input("Enter the title of the note to edit: ")
    c = conn.cursor()
    c.execute("SELECT title, note FROM general_notes WHERE title = ?", (title,))
    row = c.fetchone()
    if not row:
        print("Note not found.")
        return
    old_note = fernet.decrypt(row[1]).decode()
    print(f"Current content:\n{old_note}")
    new_note = input("New content: ")
    encrypted_note = fernet.encrypt(new_note.encode())
    c.execute("UPDATE general_notes SET note = ? WHERE title = ?", (encrypted_note, title))
    conn.commit()
    print("Note updated!")

def delete_note(conn):
    title = input("Enter the title of the note to delete: ")
    c = conn.cursor()
    c.execute("DELETE FROM general_notes WHERE title = ?", (title,))
    if c.rowcount == 0:
        print("Note not found.")
    else:
        conn.commit()
        print("Note deleted!")

# Main Program
def main():
    secret_key, master_password = load_or_create_key()
    decrypt_db(secret_key)
    fernet = Fernet(secret_key)
    conn = init_db()

    while True:
        print("\nOptions:")
        print("1. Add password")
        print("2. View all passwords")
        print("3. Search password/username/site")
        print("4. Edit password")
        print("5. Delete password")
        print("6. Add general note")
        print("7. View general notes")
        print("8. Edit general note")
        print("9. Delete general note")
        print("10. Exit")

        choice = input("Select option: ")

        if choice == "1":
            add_password(conn, fernet)
        elif choice == "2":
            view_passwords(conn, fernet)
        elif choice == "3":
            search_password(conn, fernet)
        elif choice == "4":
            edit_password(conn, fernet)
        elif choice == "5":
            delete_password(conn)
        elif choice == "6":
            add_note(conn, fernet)
        elif choice == "7":
            view_notes(conn, fernet)
        elif choice == "8":
            edit_note(conn, fernet)
        elif choice == "9":
            delete_note(conn)
        elif choice == "10":
            break
        else:
            print("Invalid option!")

    conn.close()
    encrypt_db(secret_key)
    print("Database encrypted. Goodbye!")

if __name__ == "__main__":
    main()


