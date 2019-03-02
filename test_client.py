#!/usr/bin/env python3

"""
A simple echo client
"""

import socket, pickle, hashlib
from cryptography.fernet import Fernet

def pack_question(key, text):
    f = Fernet(key)
    encoded_q = text.encode('utf-8')
    encrypted_q = f.encrypt(encoded_q)

    checksum = hashlib.md5(encrypted_q).hexdigest()

    unpickled_payload = (key, encrypted_q, checksum)

    picked_payload = pickle.dumps(unpickled_payload)

    return picked_payload

def unpack_answer(key, data):
    unpicked_payload = pickle.loads(data)
    encrypted_a, server_checksum = unpicked_payload
    client_checksum = hashlib.md5(encrypted_a).hexdigest()
    if(client_checksum != server_checksum):
        return False, "Error: did not receive the full answer."

    f = Fernet(key)
    decrypted_a = f.decrypt(encrypted_a)
    decoded_a = decrypted_a.decode('utf-8')

    return decoded_a

# MAIN PROGRAM BELOW

key = Fernet.generate_key()

host = ''
port = 55555
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

text_question = "How high can ducks fly?"

payload = pack_question(key, text_question)

s.send(payload)

data = s.recv(size)
s.close()
answer = unpack_answer(key, data)
print ('Received:', answer)