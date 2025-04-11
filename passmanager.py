import sys
import pyperclip
import argparse
from core.generator import *
from core.checker import *

class PasswordManager():
    def __init__(self,password):
        self.passwordChecker = PassChecker(password)
        self.password  = password
    # def isFoundInBreach(self):

    #     return
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
            generatedPassword = self.generateStrongPassword()
            pyperclip.copy(generatedPassword)
            return f"We suggest you to use the following password: {generatedPassword}. It has been copied to you clipboard."
        else:
            pyperclip.copy(self.password)
            return "This password not found in data breaches. Password has been copied to clipboard."


if __name__=="__main__":
    for arg in sys.argv[1:]:
        pwManager = PasswordManager(arg)
        outpt = pwManager.evaluatePassword()
        print(outpt)
