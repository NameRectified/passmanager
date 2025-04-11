import hashlib
import requests

class PassChecker():
    def __init__(self,password):
        self.password = password
    def convertToHash(self):
        hash = hashlib.sha1(self.password.encode('utf-8')).hexdigest().upper()
        return hash
    def getHeadAndTail(self):
        hash = self.convertToHash()
        # only the first 5 characters are required for the api
        head, tail = hash[:5],hash[5:]
        return head, tail
    # def breachCount(self,hashes,hashToCheck):


    def getBreachCount(self):
        head, tail = self.getHeadAndTail()
        url = 'https://api.pwnedpasswords.com/range/' + head
        result = requests.get(url)
        if result.status_code!=200:
            raise RuntimeError(f"Trouble fetching. {result.status_code}")
        else:
            hashes = (line.split(':') for line in result.text.splitlines())
            for hash, count in hashes:
                if hash==tail:
                    return count
            return 0
            # return self.breachCount(result,tail)
