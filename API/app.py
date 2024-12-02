from flask import Flask,request,jsonify
import pymongo, os
from pymongo import MongoClient,server_api
import uuid
from function import userIdGen

app = Flask(__name__)

@app.route('/')
def hello():
    return "WELCOME TO THE SERVER"


@app.route('/extract', methods=['GET'])
def extract_summary():
    requested_data = request.get_json() #expects atriclie number and its parameter i.e ["title, summary, descriptioon"]
    if not requested_data or "article_num" not in requested_data or "key_param" not in requested_data:
        return jsonify({"Error: invalid parameters or empty data sent"}), 400
    article_num = requested_data["article_num"]
    key_param = requested_data["key_param"]
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


@app.route("/insert", methods= ['POST'])
def insertdocs():
    '''
    #take username and aage as param andq assign a userid.
    # henceforth user id shall be used to filtera and update data.
    '''
    requested_data = request.get_json()
    if "username" not in requested_data or  "age" not in requested_data:
        return jsonify({"Error: invalid parameters or usename invalid"}), 400
    username = requested_data["username"]
    age = requested_data["age"]
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
    '''
    updates the user score
    '''
    requested_data = request.get_json() #expects a json with userid and score in it. a score to be added
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

@app.route('/progress',methods=['POST'])
def set_map():
    '''
    this function takes a unique userid as param and sets
    the assesed area as true to mark down the progess. initially all the map are set to false
    '''
    requested_data = request.get_json() #a json consisting of param  userid, organ, area as str
    organ = requested_data["organ"]
    area = requested_data["area"]
    userid = requested_data["userid"]
    client = None
    try:
        url = os.getenv('MONGO_URL')
        if not url:
            return jsonify({"error": "NO URL FOUND"}), 500
        client = MongoClient(url, server_api=pymongo.server_api.ServerApi(
            version="1", strict=True, deprecation_errors=True))
        database = client["constitution"]
        collection = database["user_data"]
        collection.update_one(filter={"userid":userid},update={"$set":{f"map.{organ}.area_progress.{area}":True}})
        return " ", 204
    except Exception as e:
        error_mssg = jsonify({"result": f"some unwanted Error occured: --> {e}"})
        print(error_mssg)
        return error_mssg
    finally:
        if client:
            client.close()





if __name__ == "__main__" :
    app.run(debug=True)