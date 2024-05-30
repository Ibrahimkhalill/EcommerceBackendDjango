import random
import string

def generate_otp(length=5):
    digits = string.digits
    return ''.join(random.choices(digits, k=length))