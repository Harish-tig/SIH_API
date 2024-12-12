from flask import Flask,request,jsonify
import pymongo, os
from pymongo import MongoClient,server_api
from function import userIdGen
from random import shuffle
import random
# import pprint

app = Flask(__name__)

#todo:
'''
reading material ka api.
fetching tip of the day api ✅
card api ✅
article progress update api ✅
progress api ✅
language translation api
'''

@app.route('/')
def hello():
    return "WELCOME TO THE SERVER"


@app.route('/extract', methods=['GET'])
def extract_summary():
    requested_data = request.get_json() #expects {atriclie_num,key_param }and its parameter i.e ["title, summary, description"]
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
    #take username and age as param and assign a userid.
    # henceforth user id shall be used to filtera and update data.
    # username, age
    #todo -- > change something
    '''
    requested_data = request.get_json()
    if "username" not in requested_data or  "age" not in requested_data:
        return jsonify({"Error: invalid parameters or usename invalid"}), 400
    username = requested_data["username"]
    age = requested_data["age"]
    #todo: add test data to the database to unlock new area (imp)
    docs = {
        "username": username,
        "age": age,
        "userid": userIdGen(), #works well
        "score": 0,
        "map": {
            "executive": {
                "progress": 0,
                "area_progress":{
                 "ex_a1": False,
                 "ex_a2": False,
                 "ex_a3": False,
                 "ex_a4": False
                },
                "article_progress": {
                    "completed": 0,
                    "target": 42
                }
            },
            "legislative": {
                "progress": 0,
                "area_progress":{
                 "lg_a1": False,
                 "lg_a2": False,
                 "lg_a3": False,
                 "lg_a4": False
                 },
            "article_progress": {
                    "completed": 0,
                    "target": 89
                }
            },
            "judiciary": {
                "progress": 0,
                "area_progress":{
                 "jd_a1": False,
                 "jd_a2": False,
                 "jd_a3": False,
                 "jd_a4": False
                },
                "article_progress": {
                    "completed": 0,
                    "target": 48
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
        return jsonify({"userid":docs["userid"]}), 201
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
    expects {userid,score}
    '''
    requested_data = request.get_json() #expects a json with userid and score in it. a score to be added
    if not requested_data or "userid" not in requested_data or "score" not in requested_data:
        return jsonify({"Error: invalid parameters or userid invalid"}), 400
    userid = requested_data['userid'] #todo: update to userid from user_id
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
    expects {organ,area,user_id} {organ --> legislative,executive,..etc and area --> ex_a1,ex_2}
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

@app.route("/leaderboard",methods = ['GET'])
def leaderboard():
    client = None
    try:
        url = os.getenv("MONGO_URL")
        if not url:
            return jsonify({"error":"NO URL FOUND"}), 400

        client = MongoClient(url, server_api=pymongo.server_api.ServerApi(
            version="1", strict=True, deprecation_errors=True))
        database = client["constitution"]
        collection = database["user_data"]
        lead_board = list(collection.
                      find({},{'_id':0,"username":1,"score":1})
                      .sort([("score", -1)]).limit(3))
        return jsonify({"leaderboard": lead_board}), 200
    except Exception as e:
        error_mssg = jsonify({"result": f"some unwanted Error occured: --> {e}"})
        print(error_mssg)
        return error_mssg
    finally:
        if client:
            client.close()


@app.route("/dialogue", methods=["GET"])
def dialogue():
    request_data = request.get_json()  # {"area": "base_map", "map":"ex_1" }
    # Check if 'area' is in request data
    if "area" not in request_data:
        return jsonify({"error": "Invalid parameters or user ID invalid"}), 400
    area = request_data["area"]
    map = request_data["map"]
    client = None
    try:
        url = os.getenv("MONGO_URL")
        if not url:
            return jsonify({"error": "No MongoDB URL found"}), 400
        client = MongoClient(url,
                             server_api=pymongo.server_api.
                             ServerApi(version="1", strict=True, deprecation_errors=True))
        database = client["constitution"]
        collection = database["base_map_dialogue"]
        # Query the collection for the specified 'area' and include the 'base_map'
        data_cursor = collection.find({"area": area}, {map: 1,"_id":0})
        data = list(data_cursor)
        return jsonify(data[0]),200
    except Exception as e:
        # Handle unexpected errors
        error_message = f"Some unexpected error occurred: {e}"
        print(error_message)  # Print error message for debugging purposes
        return jsonify({"error": error_message}), 500
    finally:
        # Close the MongoDB client
        if client:
            client.close()


@app.route("/minigame",methods=["GET"])
def minigame():
    requested_data = request.get_json() #request {"collection":"card,quiz,hall_meeting","area":"ex","test":"quiz_ex_1"}
    if "area" not in requested_data or "test" not in requested_data or "collection" not in requested_data:
        return jsonify({"error": "Invalid parameters"}), 400
    area = requested_data["area"]
    test = requested_data["test"]
    collection = requested_data["collection"]
    client = None
    try:
        url = os.getenv("MONGO_URL")
        if not url:
            return jsonify({"error": "No MongoDB URL found"}), 400
        client = MongoClient(url,
                             server_api=pymongo.server_api.
                             ServerApi(version="1", strict=True, deprecation_errors=True))
        database = client["constitution"]
        collection = database[collection]
        data_cursor = list(collection.find({"area": area},
                                      {"_id": 0, "area": 0}))[0] ##only one element

        data = data_cursor[test]
        print(data)
        for each_question in data:
            shuffle(each_question["options"])

        return jsonify({"data":data}), 200
    except Exception as e:
        # Handle unexpected errors
        error_message = f"Some unexpected error occurred: {e}"
        print(error_message)  # Print error message for debugging purposes
        return jsonify({"error": error_message}), 500
    finally:
        # Close the MongoDB client
        if client:
            client.close()


@app.route("/fact",methods=['GET'])
def fact():
    client = None
    try:
        url = os.getenv("MONGO_URL")
        if not url:
            return jsonify({"error": "No MongoDB URL found"}), 400
        client = MongoClient(url,
                             server_api=pymongo.server_api.
                             ServerApi(version="1", strict=True, deprecation_errors=True))
        database = client["constitution"]
        collection = database["fact"]
        data = list(collection.find({'Doc': "facts"}, {"_id": 0, "facts": 1}))[0]
        index = random.randint(0, (len(data['facts'])-1))
        return jsonify({'data':data['facts'][index]}), 200
    except Exception as e:
        # Handle unexpected errors
        error_message = f"Some unexpected error occurred: {e}"
        print(error_message)  # Print error message for debugging purposes
        return jsonify({"error": error_message}), 500
    finally:
        # Close the MongoDB client
        if client:
            client.close()


@app.route("/updateprogress",methods= ["POST"])
def updateprogress(): #{"userid":"something","map":"executive","progress":int}

    requested_data = request.get_json()

    if "userid" not in requested_data or "map" not in requested_data or "progress" not in requested_data:
        return jsonify({"Error: invalid parameters or empty data sent"}), 400

    userid = requested_data['userid']
    map = requested_data['map']
    progress = requested_data["progress"]
    if not isinstance(progress, int):
        return jsonify({"error": "Integer value expected for progress"}), 400

    client = None
    try:
        url = os.getenv("MONGO_URL")
        if not url:
            return jsonify({"error": "No MongoDB URL found"}), 400
        client = MongoClient(url,
                             server_api=pymongo.server_api.
                             ServerApi(version="1", strict=True, deprecation_errors=True))
        database = client["constitution"]
        collection = database["user_data"]

        collection.update_one({"userid": userid},
                              update={"$set": {f"map.{map}.article_progress.completed":progress}})
        data = collection.find_one({"userid": userid}, {"map": 1, "_id": 0, })
        completed = data['map'][map]["article_progress"]["completed"]
        target = data['map'][map]["article_progress"]["target"]
        collection.update_one({"userid": userid},update={"$set":{f"map.{map}.progress": round((completed / target) * 100)}})
        return " ", 204

    except Exception as e:
        # Handle unexpected errors
        error_message = f"Some unexpected error occurred: {e}"
        print(error_message)  # Print error message for debugging purposes
        return jsonify({"error": error_message}), 500
    finally:
        # Close the MongoDB client
        if client:
            client.close()


@app.route("/reading_material",methods=["GET"])
def reading_material():
    requested_data = request.get_json()
    #takes some parameter. {"area":"ex", "map" : "ex_a1"}

    if "area" not in requested_data or "map" not in requested_data:
        return jsonify({"Error: invalid parameters or empty data sent"}), 400

    area = requested_data["area"]
    map = requested_data["map"]

    client = None
    try:
        url = os.getenv("MONGO_URL")
        if not url:
            return jsonify({"error": "No MongoDB URL found"}), 400
        client = MongoClient(url,
                             server_api=pymongo.server_api.
                             ServerApi(version="1", strict=True, deprecation_errors=True))
        database = client["constitution"]
        collection = database["reading_material"]
        data = list(collection.find({"area":area}, {map:1,"_id":0}))

        return jsonify(data[0]), 200

    except Exception as e:
        # Handle unexpected errors
        error_message = f"Some unexpected error occurred: {e}"
        print(error_message)  # Print error message for debugging purposes
        return jsonify({"error": error_message}), 500
    finally:
        # Close the MongoDB client
        if client:
            client.close()



if __name__ == "__main__" :
    app.run(debug=True)