from flask import Flask, render_template, jsonify
from db.data_access import SQLiteConnection

#Creates SQLiteConnection object to access database
db = SQLiteConnection(".\\db\\dealride.sqlite3");

app = Flask(__name__, static_url_path='', 
            static_folder='web/static', 
            template_folder='web/template');

#Main Route for serving html template
@app.route("/")
def index():
    return render_template("index.html");
            
#API Route for serving vehicle positions
@app.route("/getVehicles")
def getVehicles():
            vehicles = db.getAllVehicles()
            return jsonify(vehicles)


