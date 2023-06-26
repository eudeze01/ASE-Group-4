from flask import Flask, render_template, jsonify, request
from werkzeug.exceptions import BadRequest,BadGateway
from collections import namedtuple
import json
import requests
from dotenv import load_dotenv
import os


from db.data_access import SQLiteConnection
from BusinessLayer.notuber import NotUber

#Creates SQLiteConnection object to access database
db = SQLiteConnection(".\\db\\notuberdb.sqlite3");
#Create Business Logic Layer
bl = NotUber();

app = Flask(__name__, static_url_path='', 
            static_folder='web/static', 
            template_folder='web/template');

# Main Route for serving html template
@app.route("/")
def index():
    return render_template("index.html");

# API Route for serve vehicle positions
@app.route("/getVehicles")
def getVehicles():
    vehicles = db.getAllVehicles(exludeBooked=True)
    return jsonify(vehicles)

@app.route("/api/book", methods=['post'])
def book():

    flaskReq_params = request.get_json();

    if 'source' not in flaskReq_params or 'x' not in flaskReq_params['source'] or 'y' not in flaskReq_params['source']:
        raise BadRequest("Request body doesn't have 'source':\{'x':lat, 'y':lng\} properly defined")

    freeVechicles = db.getAllVehicles(True);
    closest = bl.getClosestVehicle(
        {'x':flaskReq_params['source']['x'], 'y':flaskReq_params['source']['y']},
        freeVechicles)
    
    if 'car_id' in closest:
        db.book(closest['car_id'], flaskReq_params['source']['x'],
                flaskReq_params['source']['y'], 
                flaskReq_params['destination']['x'],
                flaskReq_params['destination']['y'])
    
    return jsonify(closest)

@app.route("/api/reset", methods=['get'])
def reset():
    db.resetDataState();
    return "Success", 200



#Error Handling
@app.errorhandler(404)
def not_found_error(e):
    response = e.get_response()

    response.data = json.dumps({'error':{
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }})
    response.content_type = "application/json"
    return response

@app.errorhandler(BadRequest)
def bad_request_error(e):
    response = e.get_response()

    response.data = json.dumps({'error':{
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }})
    response.content_type = "application/json"
    return response

    