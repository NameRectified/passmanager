import sys
import pyperclip
import argparse

from core.generator import *
from core.checker import *

class PasswordManager():
    def __init__(self,password):
        self.passwordChecker = PassChecker(password)
        self.password  = password
    def displayIfInBreach(self,count):
        '''
            If the password is found in a breach, display the number of times it was breached.
        '''
        return f"Password was found in a data breach {count} times."

    def generateStrongPassword(self,length=10):
        passwordGenerator = PassGenerator(length)
        return passwordGenerator.generate()
    def evaluatePassword(self):
        count = self.passwordChecker.getBreachCount()
        if count:
            print(self.displayIfInBreach(count))
            # generatedPasswordDisplay = self.generateStrongPassword()
            # pyperclip.copy(generatedPassword)
            return self.generateStrongPassword()
        else:
            pyperclip.copy(self.password)
            return "This password not found in data breaches. Password has been copied to clipboard."


def handle_check(args):
    pwManager = PasswordManager(args.password)
    outpt = pwManager.evaluatePassword()
    print(outpt)

def handle_generate(args):
    passwordGenerator = PassGenerator(args.length)
    print(passwordGenerator.generate())
if __name__=="__main__":
    parser = argparse.ArgumentParser(prog="passmanager")
    subparsers = parser.add_subparsers(
        title="subcommands", help="password manager functions"
    )
    checkParser = subparsers.add_parser("check",help="Checks if the password has been found in any breach")
    checkParser.add_argument("password",help="The password to check for breaches")
    checkParser.set_defaults(func=handle_check)

    generateParser = subparsers.add_parser("generate",help="Generates a strong password and copies to clipboard")
    generateParser.add_argument("-l","--length",default=10,help="Specify the length of the password.")
    generateParser.set_defaults(func=handle_generate)
    args = parser.parse_args()
    args.func(args)
    # for arg in sys.argv[1:]:
