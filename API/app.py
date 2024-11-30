from flask import Flask,request,jsonify
import pymongo, os
from pymongo import MongoClient,server_api


app = Flask(__name__)

@app.route('/')
def hello():
    return "WELCOME TO THE SERVER"



@app.route('/data', methods=['GET'])
def data():
    try:
        url = os.getenv('MONGO_URL')
        client = MongoClient(url, server_api=pymongo.server_api.ServerApi(
            version="1", strict=True, deprecation_errors=True))
        database = client["constitution"]
        collection = database["base_article"]
        result = collection.find_one({'article': 151}, {"summary": 1, "_id": 0})
        print(result['summary'])
        if result:
            return jsonify(result["summary"]), 200
        else:
            return jsonify({"message": "Article not found"}), 404

    except Exception as e:
        print(e)

@app.route('/extractSummary/<int:article_num>/<string:key_param>', methods=['GET'])
def extractSummary(article_num:int,key_param:str):
    client = False
    try:
        url = os.getenv('MONGO_URL')
        if not url:
            return jsonify({"error":"NO URL FOUND"}), 500
        client = MongoClient(url, server_api=pymongo.server_api.ServerApi(
            version="1", strict=True, deprecation_errors=True))
        database = client["constitution"]
        collection = database["base_article"]
        result = collection.find_one({'article': article_num}, {f'{key_param}': 1, "_id": 0})
        print(result[f'{key_param}'])
        if key_param in ['title','summary','description']:
            if result:
                return jsonify(result[f'{key_param}']), 200
            else:
                return jsonify({"message": "Article not found"}), 404
        else:
            return jsonify({"message": "Article not found or invalid parameter"}), 404
    except Exception as e:
        error_mssg = jsonify({"result": f"some unwanted Error occured: --> {e}"})
        print(error_mssg)
        return error_mssg
    finally:
        if client:
            client.close()
