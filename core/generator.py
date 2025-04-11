import string
import secrets
import pyperclip
class PassGenerator():
    characters = string.ascii_letters + string.digits + string.punctuation
    def __init__(self,length):
        self.length = int(length)
    def generate(self):
        # length = getValidLength()
        while True:
            password = ''.join(secrets.choice(self.characters) for _ in range(self.length))
            if (any(c.islower() for c in password)
            and  any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password)>=3):
                break
        pyperclip.copy(password)
        return f"We suggest the following password: {password}. It has been copied to you clipboard."
