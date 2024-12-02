from flask import Flask,request,jsonify
import pymongo, os
from pymongo import MongoClient,server_api
import uuid

app = Flask(__name__)

@app.route('/')
def hello():
    return "WELCOME TO THE SERVER"


@app.route('/extract/<int:article_num>/<string:key_param>', methods=['GET'])
def extract_summary(article_num:int,key_param:str):
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
def insertdocs(username:str,age:int):  #take user name and aage as param andq assign a userid.
                                   # henceforth user id shall be used to filtera and update data.
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
            },
            "legislative": {
                "area_progress":{
                 "lg_a1": False,
                 "lg_a2": False,
                 "lg_a3": False,
                 "lg_a4": False
                 },
            },
            "judiciary": {
                "area_progress":{
                 "jd_a1": False,
                 "jd_a2": False,
                 "jd_a3": False,
                 "jd_a4": False
                },
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
        return jsonify({"data":"inserted"}), 201
    except Exception as e:
        error_mssg = jsonify({"result": f"some unwanted Error occured: --> {e}"})
        print(error_mssg)
        return error_mssg
    finally:
        if client:
            client.close()


@app.route("/score",methods=["POST"])
def update_score():
    requested_data = request.get_json()
    if not requested_data or "user_id" not in requested_data or "score" not in requested_data:
        return jsonify({"Error: invalid parameters or userid invalid"}), 400
    userid = requested_data['user_id']
    point = requested_data['score']
    client = None
    try:
        url = os.getenv('MONGO_URL')
        if not url:
            return jsonify({"error":"NO URL FOUND"}), 500
        client = MongoClient(url, server_api=pymongo.server_api.ServerApi(
            version="1", strict=True, deprecation_errors=True))
        database = client["constitution"]
        collection = database["user_data"]
        d_score = collection.find_one({"userid":f"{userid}"},{"score":1,"_id":0})
        new_score = d_score['score'] + point
        collection.update_one(filter={"userid":f"{userid}"},update={"$set":{"score":new_score}}) #userid
        return  jsonify({"data":"updated"}), 201
    except Exception as e:
        error_mssg = jsonify({"result": f"some unwanted Error occured: --> {e}"})
        print(error_mssg)
        return error_mssg
    finally:
        if client:
            client.close()

@app.route('/progress/<string:organ>/<string:area>',methods=['POST'])
def set_map(organ:str,area:str):
    username = request.args.get("username")
    client = None
    try:
        url = os.getenv('MONGO_URL')
        if not url:
            return jsonify({"error": "NO URL FOUND"}), 500
        client = MongoClient(url, server_api=pymongo.server_api.ServerApi(
            version="1", strict=True, deprecation_errors=True))
        database = client["constitution"]
        collection = database["user_data"]
        collection.update_one(filter={"username":username},update={"$set":{f"map.{organ}.area_progress.{area}":True}})
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


if __name__ == "__main__" :
    app.run(debug=True)