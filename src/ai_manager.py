import random
import string

def generate_tag(num_tags=3, k=6):
    return ">".join("".join(random.choices(string.ascii_lowercase, k=k)) for _ in range(num_tags))
