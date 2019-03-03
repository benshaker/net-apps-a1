# Networking Applications Assignment 1
# Team 13, Spring 2019

The objectives of Assignment 1 required two Raspberry Pis to communicate with each other. One Pi is to act as the Server, and the other is to act as the Client. The Server Pi is essentially responsible for three tasks: 1) receiving a question from the Client Pi, 2) speaking the question “aloud” (as an audio output), and 3) requesting an answer from Wolfram|Alpha which it should pass back to the Client Pi. The Client Pi is also essentially responsible for three tasks: 1) converting a QR code into a text question, 2) pass the question to the Server Pi and wait for a response, and 3) speak the aloud answer it has received. There are a some additional, minor considerations: most importantly, the data passed between the Client and Server Pis is to be encrypted.

## Getting Started

This readme will help you get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This code requires Python3. This system is intended to be run on two separate Raspberry Pis (one Server and one Client each), although it may be run locally as a proof of concept.

You'll also need quite a few libraries to get started with this codebase. To name a few:

* [OpenCV](https://maven.apache.org/) - Used for camera capture
* [ZBAR](https://rometools.github.io/rome/) - Used for QR decoding
* [Fernet](https://cryptography.io/en/latest/fernet/) - Used for data encrpytion
* [Wolfram|Alpha](https://pypi.org/project/wolframalpha/) - Used for Q&A
* [IBM Watson](https://cloud.ibm.com/apidocs/text-to-speech?code=python) - Used for Text-to-Speech

### Installing

As with running any new Python code, you'll quickly know whether or not your environment is lacking libraries.

Installing a library is as simple as running a line such as:

```
pip3 install watson_developer_cloud
```

Of all the libraries we use, OpenCV will probably give you the most issues - primarily in that it has A Lot of dependencies. Following [this Github issue](https://github.com/bennuttall/piwheels/issues/94) helped us get OpenCV fulling operational.

Other than the libraries found in the client.py and server.py, there are no resources needed that your Raspberry Pi should not already provide.

## Deployment

Deploying this code onto a live system is relatively easy. For each Raspberry Pi, you need only its associated files (i.e. server.py requires ServerKeys.py, and the same for the client). Upon starting the Server,

```
python3 server.py -sp 55555 -z 1024
```

you will see some checkpoints have been reached. At this point, the Server is waiting for a Client connection, which can be achieved via

```
python3 client.py -sip 127.0.0.1 -sp 55555 -z 1024
```

where 127.0.0.1 should be replaced with the local IP address of the Server with which the Client should be connected. At this point, the Client may choose to send any number of decoded QR messages to the Server with hopes of getting a valid response.

## Built With

These developments are intended for the Raspberry Pi 3 B+.

* [Python3](http://www.dropwizard.io/1.0.2/docs/) - The web framework used


## Contributing

Feel free to submitting pull requests for our review.

## Authors

* **Steven Trieu** - *Initial work* - [Github](https://github.com/stevent7)
* **Christina Lin** - *Initial work* - [Github](https://github.com/intuitionally)
* **Benjamin Shaker** - *Initial work* - [Github](https://github.com/benshaker), [Personal](http://www.benshaker.com/)

## License

No license for this particular project, only those aggregated licenses of the software libraries we chose.

## Acknowledgments

* Thank you to all the folks at StackOverflow
* Thank you to our helpful and understanding TA Mihir Kulkarni
