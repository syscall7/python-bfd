from hashlib import sha1


def sha1_hash(fh):
    fh.seek(0)
    s = sha1()
    while True:
        data = fh.read(8192)
        if not data:
            break
        s.update(data)
    fh.seek(0)
    return s.hexdigest()

def sha1_hash_contents(data):
    s = sha1()
    s.update(data)
    return s.hexdigest()


import string
import random
def id_generator(size=8, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for x in range(size))