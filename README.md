# PassManager

PassManager is a simple command-line tool written in Python for managing passwords.

It allows you to:
- Check if a password has been compromised in known data breaches.
- Generate strong, secure passwords.
- Automatically copy passwords to your clipboard for convenience.

---

## Installation & Usage

1. **Clone the repository and install dependencies**:

```bash
git clone https://github.com/NameRectified/passmanager.git
cd passmanager
pip install -r requirements.txt
```

Or manually install the required packages:

```bash
pip install pyperclip requests
```

---

## Commands

### Check if a password has been breached

```bash
python passmanager.py check yourpassword123
```

Example output:

```
Password was found in a data breach 120 times.
We suggest the following password: a!92JKlm%Xq1. It has been copied to your clipboard.
```

If the password was not found in any breach:

```
This password not found in data breaches. Password has been copied to clipboard.
```

---

### Generate a strong password

```bash
python passmanager.py generate -l 20
```

- `-l` or `--length`: Optional. Specifies the length of the generated password (default is 10).

Example output:

```
We suggest the following password: aE$93kfL!xZm20!. It has been copied to your clipboard.
```

---

## How It Works

- Utilizes the [Have I Been Pwned API](https://haveibeenpwned.com/API/v3#PwnedPasswords) to safely check if a password has been compromised, using a k-anonymity approach.
- Uses Python's `secrets` and `string` modules to generate strong, random passwords.
- Clipboard functionality is managed through `pyperclip`.

---

## Requirements

- Python 3.6 or higher
- `requests`
- `pyperclip`


## License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it as needed.


## Security Note
This script follows best practices by never sending the full password or full hash over the internet. However, for maximum security, avoid testing highly sensitive passwords on any third-party service.


