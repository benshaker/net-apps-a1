#!/usr/bin/env python3

import socket
import argparse
import sys
import numpy as np
import cv2
import picamera
import time
from pyzbar.pyzbar import decode
from PIL import Image
from ClientKeys import ibm_watson_api_key
from watson_developer_cloud import TextToSpeechV1
import os
import pickle
import hashlib
from cryptography.fernet import Fernet

def main(args):

    # Label the server connection specifications
    server_ip = args.server_ip
    server_port = args.server_port
    socket_size = args.socket_size
    s = None

    # Attempt a connection to the server
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("[Checkpoint 01] Connecting to", server_ip, "on port", server_port)
        s.connect((server_ip, server_port))
    except socket.error as message:
        if s: s.close()
        print("Unable to open the socket: " + str(message))
        sys.exit(1)

    # initializing IBM Watson Text-to-Speech module
    watson_client = TextToSpeechV1(
        iam_apikey=ibm_watson_api_key,
        url='https://gateway-wdc.watsonplatform.net/text-to-speech/api'
    )

    # prepare a key for msg encryption / decryption
    key = Fernet.generate_key()

    # If there is no QR Code, then decode will output: []
    # Else there will be data, type, etc
    # Initialize the camera stream
    # cam = cv2.VideoCapture(0)
    # question = decode(cv2.imread('Hello_World_QR.png'))
    print("[Checkpoint 02] Listening for QR codes from RPi Camera that contains questions")

    question = b'What time is it?'
    print("[Checkpoint 03] New question:", question)

    # pack initial msg for Server
    payload = pack_question(key, question.decode("utf-8"))
    # print (cam.isOpened())

    # Continually scan for questions
    while True:

        # Grab a frame from the stream
        # ret, frame = cam.read()
        # Convert the image to grayscale
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Decode the QR code
        # question = decode(gray)

        # If there was no readable QR code, then retry
        # s.send(question.data)

        # send data to Server
        print("[Checkpoint 05] Sending data:", payload)
        s.send(payload)

        # await data from Server
        data = s.recv(socket_size)
        print("[Checkpoint 06] Received data:", data)

        # unpack data from Server
        answer_text = unpack_answer(key, data)

        # speak question text aloud
        speak_aloud(watson_client, answer_text)
        break

    # close this socket connection
    s.close()

def pack_question(key, text):

    # encode the text
    encoded_q = text.encode('utf-8')

    # encrypt the question with the new key
    encrypted_q = Fernet(key).encrypt(encoded_q)
    print("[Checkpoint 04] Encrypt: Generated key:", key, "| Ciphertext:", encrypted_q)

    # generate a checksum for the Server's reference
    checksum = hashlib.md5(encrypted_q).hexdigest()

    # prepare the payload for pickling
    unpickled_payload = (key, encrypted_q, checksum)

    # pickle the payload
    picked_payload = pickle.dumps(unpickled_payload)

    return picked_payload

# this function unpickles, unencrypts, and deciphers the Server's answer
# returns decoded_a
# @decoded_a: string type containing error or answer text
def unpack_answer(key, data):
    # unpickle the payload
    unpicked_payload = pickle.loads(data)

    # unpackage the unpickled payload
    encrypted_a, server_checksum = unpicked_payload

    # compare checksums: my hash should equal the one sent
    client_checksum = hashlib.md5(encrypted_a).hexdigest()
    if client_checksum != server_checksum:
        return False, "Error: did not receive the full answer."

    # decrypt the answer with the original key
    decrypted_a = Fernet(key).decrypt(encrypted_a)
    print("[Checkpoint 07] Decrypt: Using key:", key, " | Plaintext:", decrypted_a)

    # decode the text
    decoded_a = decrypted_a.decode('utf-8')

    return decoded_a

# this function sends plain text to Watson for conversion to soundwaves
def speak_aloud(client, text):
    # create an audio file from the text
    with open('speech.wav', 'wb') as audio_file:
        audio_file.write(
            client.synthesize(
                text,
                'audio/wav',
                'en-GB_KateVoice'
            ).get_result().content)

    print("[Checkpoint 08] Speaking answer:", text)
    # play that audio file like any other
    os.system("omxplayer speech.wav > /dev/null")
    return None

if __name__ == "__main__":

    # initialize management of command line parameters
    parser = argparse.ArgumentParser(description='Sends questions to the Server with hopes of hearing an answer.')

    parser.add_argument('--server_ip',
                        '-sip',
                        help="The IP address of the Server to receive the encrypted question",
                        type=str)

    parser.add_argument('--server_port',
                        '-sp',
                        help="The Server Port this Client will try connecting to",
                        type=int,
                        default=50000)

    parser.add_argument('--socket_size',
                        '-z',
                        help="the Socket Size, bytes per data packet",
                        type=int,
                        default=1024)

    # require the user input all Client.py parameters
    if len(sys.argv) != 7:
        print("Error: Too few arguments provided. Please see --help for more information.")
    else:
        main(parser.parse_args(sys.argv[1:]))
