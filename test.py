import hashlib
print(type(hashlib.sha256("test.txt".encode("utf-8")).hexdigest()))