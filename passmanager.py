import sys
import pyperclip
import argparse
from core/generator import *
from core/chcker import *

class PasswordManager():
    def __init__(self):
        self.passwordChecker = PassChecker()

    
    def isValid(self,password):
        count = self.passwordChecker.getBreachCount(password)
        if count:
            display = f"Password was found in a data breach {count} times. Would you like to generate a strong password?\nIf you wish to generate, press 1 else press enter. "
            print(display)
            userResponse = input()
            if userResponse=='':
                return f"Please change your password as it is weak."
            elif int(userResponse) == 1:
                try:
                    length = int(input("How long should the password be (min:10): "))
                    if length<10:
                        raise ValueError("Invalid length")
                    passwordGenerator = PassGenerator(length)
                    generatedPassword = passwordGenerator.generate()
                    shouldCopy = int(input("Enter 1 if you wish to copy the password to clipboard: "))
                    if shouldCopy == 1:
                        pyperclip.copy(generatedPassword)
                        print("Password successfully copied to clipboard.")
                    return f"{generatedPassword} is the generated password."

                except ValueError:
                    return ("Please enter a valid password length.")
        else:
            return f"{password} is a good password. You can use it."
