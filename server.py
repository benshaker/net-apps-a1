#!/usr/bin/env python3
# server.py

"""
A simple echo server
"""

import sys
import socket
import argparse

parser = argparse.ArgumentParser(description='Answers any incoming questions from the Client.')
parser.add_argument('--server_port', '-sp', help="the Server Port to be opened for connection", type= int)
parser.add_argument('--socket_size', '-z', help="the Socket Size, bytes per data packet", type= int, default= 1024)

args = parser.parse_args()


if(len(sys.argv) != 5):
    print("Incorrect number of arguments provided. See help via -h")
    exit()

host = ''
port = args.server_port
backlog = 5
size = args.socket_size
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)
while 1:
    client, address = s.accept()
    data = client.recv(size)
    print (b'Received : ' + data)
    if data:
        client.send(data)
    client.close()