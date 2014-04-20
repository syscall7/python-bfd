from hashlib import sha1


def sha1_hash(fh):
    #fh = open(filePath, 'rb')
    s = sha1()
    s.update("blob ")
    while True:
        data = fh.read(8192)
        if not data:
            break
        s.update(data)
    s.update("\0")
    return s.hexdigest()

import string
import random
def id_generator(size=6, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for x in range(size))