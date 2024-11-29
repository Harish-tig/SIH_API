from flask import Flask,request,jsonify
import pymongo, os
from pymongo import MongoClient,server_api


app = Flask(__name__)

@app.route('/')
def hello():
    return "WELCOME TO THE SERVER"