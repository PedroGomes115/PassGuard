

# Password Related Programs

## Password Strength 

---

---

PassGuard is a Python-based password strength analyzer designed to evaluate the security of user passwords and provide actionable feedback to improve them.

---

### Features

* Password strength scoring (0–100)
* Intelligent analysis
* Real-time feedback with improvement suggestions
* Clear classification

---

### How It Works

The program evaluates a password based on several security criteria:

* Minimum length of 12 characters
* Use of uppercase letters (A–Z)
* Use of lowercase letters (a–z)
* Inclusion of numeric digits (0–9)
* Use of special characters (e.g. !, @, #, $)

Each criterion contributes to the overall score, resulting in a final strength rating.

---

### How to Run

* Make sure Python 3 is installed on your system
* Clone this repository or download the files
* Run the program:

```bash id="a1x9kp"
python password_checker.py
```

* Enter a password when prompted

---

## PassGuard

---

---

### Features

- **Master Password Protected** – One password to unlock all others.
- **Encrypted Storage** – AES-GCM encryption ensures confidentiality and integrity.
- **Salt & Pepper Protection** – Unique salt per password plus a secret pepper.
- **Secure Key Derivation** – Argon2 makes brute-force attacks computationally expensive.
- **Cross-Platform** – Works on any system with Python 3 installed.
- **CLI Interface** – Easy-to-use command-line interface.

---

### How It Works

#### Encryption System:

1. **Master Password**: Required to access all stored passwords.
2. **Pepper**: Randomly generated, encrypted with the master password, and stored separately. Without it, the password database cannot be decrypted.
3. **Salt**: Each password gets a unique salt during encryption. It ensures that identical passwords have different encrypted values.
4. **AES-GCM**: Used for encryption to guarantee confidentiality and integrity.
5. **Argon2 KDF**: Converts master password + salt + pepper into an encryption key resistant to brute-force attacks.


---

### Installation

1. Ensure **Python 3.9+** is installed.
2. Install dependencies:

```bash
pip install cryptography
