# utils/random_utils.py
import random
import string
def generate_random_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))