#!/usr/bin/env python3
# server.py

"""
A simple echo server
"""

import sys
import socket
import argparse
import requests
from ServerKeys import wolframaplha_api_key

def main(args):



    host = ''
    port = args.server_port
    backlog = 5
    size = args.socket_size
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen(backlog)

    print("Server listening on port: ", port)
    print("Server handling packet size: ", size)
    # print one line for each queryresult.pods[i].subpods.plaintext

    while 1:
        client, address = s.accept()
        data = client.recv(size)
        print (b'Received : ' + data)
        response = ask_wolfram(data)
        print("here is your response:\n")
        print(response)
        if data:
            client.send(data)
        client.close()

def ask_wolfram(the_question):
    # TODO update decoding of the text that comes in
    # i.e., .decode should not be necessary
    input_with_spaces  = the_question.decode('utf-8')
    input_no_spaces = input_with_spaces.replace(" ", "%20")

    # TODO we may need to convert this into a promise
    # otherwise the function won't wait for this request
    # before it returns an empty answer
    r = requests.get('http://api.wolframalpha.com/v2/query?'
                        'input=' + input_no_spaces +
                        '&appid=' + wolframaplha_api_key +
                        '&output=json'
                        '&format=plaintext')
    json_res = r.json()

    query_res = json_res['queryresult']

    the_answer = "Could not find an answer to your question."
    # print(res)
    if(query_res['success'] == False):
        return the_answer

    pods = query_res['pods']

    for i in range(len(pods)):
        if 'primary' in pods[i] and pods[i]['primary'] == True:
            subpods = pods[i]['subpods']
            subpod = subpods[0]
            the_answer = subpod['plaintext']
    return the_answer


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Answers any incoming questions from the Client.')
    parser.add_argument('--server_port', '-sp', help="the Server Port to be opened for connection", type= int, default= 50000)
    parser.add_argument('--socket_size', '-z', help="the Socket Size, bytes per data packet", type= int, default= 1024)

    args = parser.parse_args()

    if(len(sys.argv) != 5):
        print("Error: Incorrect number of arguments provided. See help with --help")
    else:
        main(parser.parse_args(sys.argv[1:]))
