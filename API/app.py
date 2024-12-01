from flask import Flask,request,jsonify
import pymongo, os
from pymongo import MongoClient,server_api
import uuid


app = Flask(__name__)

@app.route('/')
def hello():
    return "WELCOME TO THE SERVER"





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


@app.route("/insert/<string:username>/<int:age>/", methods= ['POST'])
def insertdocs(username:str,age:int):
    docs = {
        "username": username,
        "age": age,
        "userid": userIdGen(), #works well
        "score": 0,
        "ex_prog": 0, # (completed/target)*100
        "leg_prog": 0,
        "jd_prog": 0,
        "map": {
            "executive": {
                "area_progress":{
                 "ex_a1": False,
                 "ex_a2": False,
                 "ex_a3": False,
                 "ex_a4": False
                },
                "article":{
                    "completed": 5,
                    "target": 46 #static #46 assumption
                }
            },
            "legislative": {
                "area_progress":{
                 "lg_a1": False,
                 "lg_a2": False,
                 "lg_a3": False,
                 "lg_a4": False
                 },
                "article":{
                    "completed": 5,
                    "target": 46  # static #46 assumption
                }
            },
            "judiciary": {
                "area_progress":{
                 "jd_a1": False,
                 "jd_a2": False,
                 "jd_a3": False,
                 "jd_a4": False
                },
                "article":{
                    "completed": 5,
                    "target": 46  # static #46 assumption
                }
            }
        }
    }
    client = None
    try:
        url = os.getenv("MONGO_URL")
        if not url:
            return jsonify({"error":"NO URL FOUND"}), 500
        client = MongoClient(url, server_api=pymongo.server_api.ServerApi(
            version="1", strict=True, deprecation_errors=True))
        database = client["constitution"]
        collection = database["user_data"]
        collection.insert_one(docs)
        print("dataSucessfully inserted!!")
        return " ", 204
    except Exception as e:
        error_mssg = jsonify({"result": f"some unwanted Error occured: --> {e}"})
        print(error_mssg)
        return error_mssg
    finally:
        if client:
            client.close()

def userIdGen():
    return uuid.uuid4().hex[:12]