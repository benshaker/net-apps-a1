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

def main(args):
	# Label the server connection specifications
	server_ip = args.sip
	server_port = args.sp
	socket_size = args.z
	s = None

	key = Fernet.generate_key()

	# Set up the server connection
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((server_ip, server_port))
	except socket.error as message:
		if s:
			s.close()
		print ("Unable to open the socket: " + str(message))
		sys.exit(1)

	# If there is no QR Code, then decode will output: []
	# Else there will be data, type, etc
	# Initialize the camera stream
	# cam = cv2.VideoCapture(0)
	# question = decode(cv2.imread('Hello_World_QR.png'))
	question = b'What time is it?'

	payload = pack_question(key, question.decode("utf-8"))
	# print (cam.isOpened())

	# initializing text-to-speech
	text_to_speech = TextToSpeechV1(
		iam_apikey=ibm_watson_api_key,
		url='https://gateway-wdc.watsonplatform.net/text-to-speech/api'
	)

	# Continually scan for questions
	while True:

		# Grab a frame from the stream
		# ret, frame = cam.read()
		# Convert the image to grayscale
		# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# Decode the QR code
		# question = decode(gray)

		# If there was no readable QR code, then retry

		s.send(payload)

		data = s.recv(socket_size)
		answer = unpack_answer(key, data)
		with open('speech.wav', 'wb') as audio_file:
			audio_file.write(
				text_to_speech.synthesize(
					answer,
					'audio/wav',
					'en-GB_KateVoice'
				).get_result().content)
		os.system("omxplayer speech.wav")
		break
	# Messages should be sent in bytes b' '
	s.close()

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-sip', help="Server IP Address", type=str)
	parser.add_argument('-sp', help="Server Port", type=int, default=0)
	parser.add_argument('-z', help="Socket Size", type=int, default=0)

	if len(sys.argv) != 7 and sys.argv[1] != "-h" and sys.argv[1] != "--help":
		print("Error: Too few arguemnts")
	else: 
		main(parser.parse_args(sys.argv[1:]))
