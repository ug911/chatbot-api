from flask import Flask, request, send_file
from flask_cors import CORS
import boto3
from urllib.parse import urlparse
import requests
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello World!'

