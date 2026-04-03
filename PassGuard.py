import re

# Banner

def banner():
    print("---------------------------------------------")
    print("                  PassGuard                  ")
    print("             Made by: Pedro Gomes            ")
    print("---------------------------------------------")
    print("")

banner()

# Core

def check_password_strength(password):
    score = 0
    suggestions = []

    # Length
    if len(password) >= 12:
        score += 20
    else:
        suggestions.append("Use at least 12 characters")

    # Uppercase
    if re.search(r"[A-Z]", password):
        score += 20
    else:
        suggestions.append("Add uppercase letters")

    # Lowercase
    if re.search(r"[a-z]", password):
        score += 20
    else:
        suggestions.append("Add lowercase letters")

    # Numbers
    if re.search(r"[0-9]", password):
        score += 20
    else:
        suggestions.append("Add numbers")

    # Special characters
    if re.search(r"[^A-Za-z0-9]", password):
        score += 20
    else:
        suggestions.append("Add special characters")

    return score, suggestions


def get_strength_label(score):
    if score < 40:
        return "Weak"
    elif score < 80:
        return "Medium"
    else:
        return "Strong"


def main():
    password = input("Enter your password: ")

    score, suggestions = check_password_strength(password)
    strength = get_strength_label(score)

    print(f"\nScore: {score}/100")
    print(f"Strength: {strength}\n")

    if suggestions:
        print("Suggestions:")
        for s in suggestions:
            print(f"- {s}")
    else:
        print("Great password! No suggestions")


if __name__ == "__main__":
    main()
