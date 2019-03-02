#!/usr/bin/env python3
# server.py

"""
A simple echo server
"""

import sys
import json
import socket
import argparse
import requests
import hashlib
import pickle
import wolframalpha
from cryptography.fernet import Fernet
from ServerKeys import wolframaplha_api_key, ibm_watson_api_key
from watson_developer_cloud import TextToSpeechV1
import os


def main(args):

    host = ''
    port = args.server_port
    backlog = 5
    size = args.socket_size
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("[Checkpoint 01] Created socket at", host, "on port", port)

    s.listen(backlog)
    print("[Checkpoint 02] Listening for client connections")

    # initializing text-to-speech
    text_to_speech = TextToSpeechV1(
        iam_apikey=ibm_watson_api_key,
        url='https://gateway-wdc.watsonplatform.net/text-to-speech/api'
    )
    print("[Checkpoint 03] Authenticated IBM Watson")

    # establish our connection with wolfram|alpha
    wa_client = wolframalpha.Client(wolframaplha_api_key)
    print("[Checkpoint 04] Established connection with Wolfram | Alpha")

    # print one line for each queryresult.pods[i].subpods.plaintext
    try:
        while True:
            client, address = s.accept()
            print("[Checkpoint 05] Accepted client connection from", client.getpeername()[0], "on port", address[1])
            data = client.recv(size)
            # print (b'Received question: ' + data)

            good_question, question_text, key = unpack_question(data)

            # speak response
            with open('speech.wav', 'wb') as audio_file:
                audio_file.write(
                    text_to_speech.synthesize(
                        question_text,
                        'audio/wav',
                        'en-GB_KateVoice'
                    ).get_result().content)
            print("[Checkpoint 08] Speaking question:", question_text)
            os.system("omxplayer speech.wav > /dev/null")

            if good_question:
                # send question off to wolfram
                answer_text = ask_wolfram(wa_client, question_text)
                print("[Checkpoint 10] Received answer from Wolfram | Alpha:", answer_text)

                # encode wolfram's response
                response = pack_answer(key, answer_text)

            if response:
                # send the response to the client
                print("[Checkpoint 13] Sending answer:", response)
                client.send(response)
            client.close()
    except KeyboardInterrupt:
        pass


def unpack_question(data):
    unpicked_payload = pickle.loads(data)
    print("[Checkpoint 06] Received data:", unpicked_payload)

    # print(unpicked_payload)
    key, encrypted_q, client_checksum = unpicked_payload
    server_checksum = hashlib.md5(encrypted_q).hexdigest()
    if client_checksum != server_checksum:
        error_text = "Error: did not receive your full question."
        return False, error_text, None

    f = Fernet(key)
    decrypted_q = f.decrypt(encrypted_q)
    decoded_q = decrypted_q.decode('utf-8')

    print("[Checkpoint 07] Decrypt: Key:", key, "| Plaintext:", decoded_q)
    return True, decoded_q, key


def pack_answer(key, text):
    f = Fernet(key)
    encoded_q = text.encode('utf-8')
    encrypted_q = f.encrypt(encoded_q)
    print("[Checkpoint 11] Encrypt: Key:", key, " | Ciphertext:", encrypted_q)

    checksum = hashlib.md5(encrypted_q).hexdigest()
    print("[Checkpoint 12] Generated MD5 Checksum:", checksum)

    unpickled_payload = (encrypted_q, checksum)

    picked_payload = pickle.dumps(unpickled_payload)

    return picked_payload


def ask_wolfram(client, question):

    # send the question to wolfram|alpha & await response
    response = client.query(question)
    print("[Checkpoint 09] Sending question to Wolfram | Alpha:", question)

    # default reply assumes no answer was found
    the_answer = "Could not find an answer to your question."

    # return default if wolfram leaves us high & dry
    if '@success' in response and response['@success'] == 'false':
        return the_answer

    # search through all responses for primary answer
    found_primary = False
    for pod in response.pods:
        for sub in pod.subpods:
            if '@primary' in sub and sub['@primary'] == 'true':
                the_answer = sub['plaintext']
                found_primary = True
                break
        if found_primary: break

    return the_answer


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Answers any incoming questions from the Client.')

    parser.add_argument('--server_port',
                        '-sp',
                        help="the Server Port to be opened for connection",
                        type=int,
                        default=50000)

    parser.add_argument('--socket_size',
                        '-z',
                        help="the Socket Size, bytes per data packet",
                        type=int,
                        default=1024)

    args = parser.parse_args()
    main(parser.parse_args(sys.argv[1:]))
