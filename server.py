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
import wolframalpha
from ServerKeys import wolframaplha_api_key
from watson_developer_cloud import TextToSpeechV1
import os

def main(args):

    host = ''
    port = args.server_port
    backlog = 5
    size = args.socket_size
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen(backlog)

    # initializing text-to-speech
    text_to_speech = TextToSpeechV1(
        iam_apikey='8tY8kV6y_CR_m3Hp0-CgQdSKldyLKu0vzunGoIg37vEe',
        url='https://gateway-wdc.watsonplatform.net/text-to-speech/api'
    )

    # establish our connection with wolfram|alpha
    wa_client = wolframalpha.Client(wolframaplha_api_key)

    print("Server listening on port: ", port)
    print("Server handling packet size: ", size)
    # print one line for each queryresult.pods[i].subpods.plaintext
    try:
        while True:
            client, address = s.accept()
            data = client.recv(size)
            print (b'Received question: ' + data)

            # need to convert from bytes to string
            question_text = data.decode('utf-8')

            # speak response
            with open('speech.wav', 'wb') as audio_file:
                audio_file.write(
                    text_to_speech.synthesize(
                        question_text,
                        'audio/wav',
                        'en-GB_KateVoice'
                    ).get_result().content)
            os.system("omxplayer speech.wav")

            # send question off to wolfram
            response = ask_wolfram(wa_client, question_text)

            # encode wolfram's response
            response = response.encode('utf-8')
            if response:
                # send the response to the client
                client.send(response)
            client.close()
    except KeyboardInterrupt:
        pass


def ask_wolfram(client, question):

    # send the question to wolfram|alpha & await response
    response = client.query(question)

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
    parser.add_argument('--server_port', '-sp', help="the Server Port to be opened for connection", type= int, default= 50000)
    parser.add_argument('--socket_size', '-z', help="the Socket Size, bytes per data packet", type= int, default= 1024)

    args = parser.parse_args()

    main(parser.parse_args(sys.argv[1:]))
