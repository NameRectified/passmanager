import hashlib
import requests

class PassChecker():
    def convertToHash(self,password):
        hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        return hash
    def getHeadAndTail(self,password):
        hash = self.convertToHash(password)
        # only the first 5 characters are required for the api
        head, tail = hash[:5],hash[5:]
        return head, tail
    def breachCount(self,hashes,hashToCheck):
        hashes = (line.split(':') for line in hashes.text.splitlines())
        for hash, count in hashes:
            if hash==hashToCheck:
                return count
        return 0

    def getBreachCount(self,password):
        head, tail = self.getHeadAndTail(password)
        url = 'https://api.pwnedpasswords.com/range/' + head
        result = requests.get(url)
        if result.status_code!=200:
            raise RuntimeError(f"Trouble fetching. {result.status_code}")
        else:
            return self.breachCount(result,tail)
