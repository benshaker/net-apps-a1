#!/usr/bin/env python3
# server.py

"""
Here we define the Server. The Server is responsible for returning answers to the Client. The questions received must first be decrypted, spoken aloud, sent off to find an answer, and an answer must be sent back through the same sort of encrpytion with which it was sent in.
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
    # initializing our server's socket
    host = ''
    backlog = 5
    port = args.server_port
    size = args.socket_size

    # configure socket to use IPV4, TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # the following line allows for graceful shutdown on keyboard interrupt
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))

    # initializing IBM Watson Text-to-Speech module
    watson_client = TextToSpeechV1(
        iam_apikey=ibm_watson_api_key,
        url='https://gateway-wdc.watsonplatform.net/text-to-speech/api'
    )

    # initializing Wolfram|Alpha Q&A module
    wolfram_client = wolframalpha.Client(wolframaplha_api_key)

    # determine current Pi's IP
    host_ip = socket.gethostbyname(socket.gethostname())
    print("[Checkpoint 01] Created socket at", host_ip, "on port", port)

    # opening our port for communications
    s.listen(backlog)
    print("[Checkpoint 02] Listening for client connections")

    try:
        # continually search for incoming connections
        while True:
            # await connection from client
            client, address = s.accept()

            ip, port = address
            print("[Checkpoint 03] Accepted client connection from ", ip,
                  " on port ", port)

            # await data from client
            data = client.recv(size)

            # unpack data from Client
            good_question, question_text, key = unpack_question(data)

            # speak question text aloud
            speak_aloud(watson_client, question_text)

            if not good_question:
                answer_text = "Could not decipher your question. Please try again."
            else:
                # send question to wolfram
                print("[Checkpoint 07] Sending question to Wolframalpha:",
                    question_text)
                answer_text = ask_wolfram(wolfram_client, question_text)
                print("[Checkpoint 08] Received answer from Wolframalpha:",
                    answer_text)

            # pack response for client
            response = pack_answer(key, answer_text)

            if response:
                # send packed response to client
                print("[Checkpoint 11] Sending answer:", response)
                client.send(response)

            # end this connection with the Client
            client.close()
    except KeyboardInterrupt:
        # exit gracefully on CTRL-C
        pass

# this function unpickles, unencrypts, and deciphers the Client's question
def unpack_question(data):
    # unpickle the paylod
    unpicked_payload = pickle.loads(data)
    print("[Checkpoint 04] Received data:", unpicked_payload)

    # break tuple into constituents
    key, encrypted_q, client_checksum = unpicked_payload

    # compare checksums: my hash should equal the one sent
    server_checksum = hashlib.md5(encrypted_q).hexdigest()
    if client_checksum != server_checksum:
        # return an error if checksums do not match
        error_text = "Error: did not receive your full question."
        return False, error_text, None

    # decrypt the question with the provided key
    decrypted_q = Fernet(key).decrypt(encrypted_q)
    print("[Checkpoint 05] Decrypt: Key:", key, "| Plaintext:", decrypted_q)

    # decode the text
    decoded_q = decrypted_q.decode('utf-8')
    return True, decoded_q, key

# this function encodes, encrpyts, and pickles the Server's answer
def pack_answer(key, text):

    # encode the text
    encoded_a = text.encode('utf-8')

    # encrypt the answer with the provided key
    encrypted_a = Fernet(key).encrypt(encoded_a)
    print("[Checkpoint 09] Encrypt: Key:", key, "| Ciphertext:", encrypted_a)

    # generate a checksum for the Client's reference
    checksum = hashlib.md5(encrypted_a).hexdigest()
    print("[Checkpoint 10] Generated MD5 Checksum:", checksum)

    # prepare the payload for pickling
    unpickled_payload = (encrypted_a, checksum)

    # pickle the payload
    picked_payload = pickle.dumps(unpickled_payload)

    return picked_payload

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

    print("[Checkpoint 06] Speaking question:", text)
    # play that audio file like any other
    os.system("omxplayer speech.wav > /dev/null")
    return None

# this function sends a question to Wolfram in hopes of getting an answer
def ask_wolfram(client, question):

    # send the question to wolfram|alpha & await response
    response = client.query(question)
    print("[Checkpoint 09] Sending question to Wolfram | Alpha:", question)

    # default reply assumes no answer was found
    the_answer = "Could not find an answer to your question."

    # return default if wolfram leaves us high & dry
    if '@success' in response and response['@success'] == 'false':
        return the_answer

    # search through all responses for the best answer
    found_primary = False
    for pod in response.pods:
        for sub in pod.subpods:
            if '@primary' in pod and pod['@primary'] == 'true':
                the_answer = sub['plaintext']
                found_primary = True
                # exit once we've found the primary answer
                break
        if found_primary: break

    return the_answer


if __name__ == "__main__":
    # initialize management of command line parameters
    parser = argparse.ArgumentParser(description='Answers any incoming questions from the Client.')

    parser.add_argument('--server_port',
                        '-sp',
                        help="the Server Port to be opened for Client connection",
                        type=int,
                        default=50000)

    parser.add_argument('--socket_size',
                        '-z',
                        help="the Socket Size, bytes per data packet",
                        type=int,
                        default=1024)

    # do not require parameters: allowing the use of defaults
    # args = parser.parse_args()
    main(parser.parse_args(sys.argv[1:]))
