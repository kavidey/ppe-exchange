import random
import string

def generate_key(length=128):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))