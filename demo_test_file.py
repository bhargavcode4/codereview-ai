def add(a,b):
    x=a+b
    return x

def divide(a, b):
    return a / b

import os

def load_data(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return f.read()
        except:
            print("Failed to read file")
            return None

