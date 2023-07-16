from flask import (Flask, 
                   render_template, 
                   jsonify, 
                   request, 
                   redirect, 
                   url_for, 
                   flash,
                   make_response)
from werkzeug.exceptions import BadRequest
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import json
import os
import re

from db.data_access import SQLiteConnection, User
from BusinessLayer.notuber import NotUber
from utilities import move1DistanceUnitAlong

# User for testing
# test_user = User(0,"john@abc.com",generate_password_hash("1234"), "John Smith")
# test_user = User(0,"riley@xyz.com",generate_password_hash("1234"), 
#                  "Riley Walker",acc_type="driver", vehicle_id="mXfkjrFw")

test_user = User(0,"admin@abc.com",generate_password_hash("1234"), "Richard Johnson",acc_type="admin");


#Creates SQLiteConnection object to access database
db = SQLiteConnection(".\\db\\notuberdb.sqlite3", test_user);
#Create Business Logic Layer
bl = NotUber();

app = Flask(__name__, static_url_path='', 
            static_folder='web/static', 
            template_folder='web/template');

app.secret_key = os.environ['APP_SECRET_KEY']

#Setting up for Login
login_manger = LoginManager(app=app)
login_manger.login_view = 'login'

@login_manger.user_loader
def load_user(user_id):
    return db.getUser(user_id, "")

#Login Route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if(request.method=='POST'):

        user_id = request.form["username"]
        pw = request.form["password"]

        user = db.getUser(user_id, pw)
        
        if(user is not None and user.is_authenticated()):
            login_user(user)
            print(request.args.get('next'))
            next = request.args.get('next')

            if(user.type =="driver"):
                return redirect(next or url_for('driverProfile'))
            elif(user.type == "admin"):
                return redirect(next or url_for('adminPanel'))
            return redirect(next or url_for('index'))
        else:
            flash("User Name/Password Wrong.")

    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

#----------- Passengers' section ------------
# Main Route for serving html template
@app.route("/")
@login_required
def index():
    resp = make_response(render_template("index.html", name=current_user))
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp;


# API Route for serve vehicle positions
@app.route("/api/getCurrentVehicles")
def getVehicles():
    vehicles = db.getAllVehicles(exludeBooked=True)
    return jsonify(vehicles)

# API Route for serve vehicle details
@app.route("/api/getVehicleDetails", methods=['GET'])
def getVehicleDetails():
    _id = request.args['id']
    vehicle = db.getVehicleDetails(_id)

    return jsonify(vehicle)

#API Route for book vehicle
@app.route("/api/book", methods=['post'])
@login_required
def book():

    flaskReq_params = request.get_json();

    if 'source' not in flaskReq_params or 'x' not in flaskReq_params['source'] or 'y' not in flaskReq_params['source']:
        raise BadRequest("Request body doesn't have 'source':\{'x':lat, 'y':lng\} properly defined")
    
    if 'destination' not in flaskReq_params or 'x' not in flaskReq_params['destination'] or 'y' not in flaskReq_params['destination']:
        raise BadRequest("Request body doesn't have 'source':\{'x':lat, 'y':lng\} properly defined")

    freeVechicles = db.getAllVehicles(True, flaskReq_params['type']);
    if len(freeVechicles)==0:
        return jsonify({})
    
    closest = bl.getClosestVehicle(
        {'x':flaskReq_params['source']['x'], 'y':flaskReq_params['source']['y']},
        freeVechicles)
    
    
    if 'car_id' in closest:
        db.book(closest['car_id'], flaskReq_params['source']['x'],
                flaskReq_params['source']['y'], 
                flaskReq_params['destination']['x'],
                flaskReq_params['destination']['y'],
                current_user.dbid,
                flaskReq_params['pathArray'])
    
    return jsonify(closest)

@app.route("/api/currentBooking", methods=['GET'])
def getCurrentBooking():
    if(isinstance(current_user, User)):
        b = db.getBookingForUser(current_user.dbid)
        if(b is not None):
            return jsonify(b)
        else:
            return {}
    return 'Unauthorized', 401

@app.route("/api/startJourney", methods=['GET'])
def startJourney():
    if(isinstance(current_user, User)):
        d = db.startJourneyForUser(current_user.dbid)
        return 'Sucess', 200
    else:
        return 'Unauthorized', 401

@app.route("/api/endJourney", methods=['POST'])
def endJourney():
    if(isinstance(current_user, User)):

        param = request.get_json();

        db.endJourneyForUser(current_user.dbid, param['fair'])
        return 'Sucess', 200
    else:
        return 'Unauthorized', 401
    
@app.route("/api/rateBooking", methods=['GET'])
def rateBooking():
    if(isinstance(current_user, User)):
        db.rateBooking(current_user.dbid,request.args['rating'])
        return 'Sucess', 200
    else:
        return 'Unauthorized', 401

@app.route("/api/previousJourneys", methods=['GET'])
def getPreviousJourneys():
    if(isinstance(current_user, User)):
        d = db.getPreviousJourneys(current_user.dbid)
        return jsonify(d)
    else:
        return 'Unauthorized', 401
    


# ---------Driver's section---------
#Route for serving html for users of type "driver"
@app.route("/driverProfile")
@login_required
def driverProfile():
    if(isinstance(current_user, User) and current_user.type=="driver"):

        vehicle_details = db.getVehicleDetails(current_user.vehicle_id);

        v_id = vehicle_details['id']
        plate = vehicle_details['plate']
        name = vehicle_details['driver_name']
        model = vehicle_details['model']
        v_type = vehicle_details['type']
        rating = -1 if vehicle_details['avg_rating']==None else round(vehicle_details['avg_rating'], 3) 
        email = current_user.id;

        return render_template('driverProfile.html', **locals())
    else:
        return login_manger.unauthorized()
    
@app.route("/api/driverJourneyHistory")
@login_required
def driverJourneyHistory():
    if(isinstance(current_user, User) and current_user.type=="driver"):
        d = db.getDriverJourneyHistory(current_user.dbid)
        return jsonify(d);
    else:
        return 'Unauthorized', 401
    


# ----------- Admin Section -----------
@app.route("/adminPanel")
@login_required
def adminPanel():
    if(isinstance(current_user, User) and current_user.type=="admin"):
        return render_template('adminPanel.html')
    else:
        return login_manger.unauthorized()
    

@app.route("/api/getAllDrivers")    
def getDriverDetails():
    # pass
    d = db.getAllDriverDetails()

    return jsonify(d);
    
@app.route("/api/getDriverJourneys")
def getDriverJourneys():
    d = db.getAllJouneys();

    return jsonify(d);

# ---------- Common Section -------------
@app.route("/api/tick")
def tick():
    # TODO : 
    # 1. Get Booked Vehicles
    # 2. foreach get polyline for journey
    # 3.  get last passed point as idx
    #    if distnce from path:idx to path:next_idx > 1km then 
    #                           interpolate between idx and next_idx
    # 4. else check the same with 
    #               from path:idx via path:next_idx to path:next_next_idx and so on.
    # 5. Update Positions

    booked = db.getOnGoingBooking()
    for rec in booked:
        # Regex to extract positions in db.booking.pathArray
        # ex : String"(1.3332, 2.344), (12.23, 34.9)" reutrns 
        # [{'lat':1.332, 'lng':2.344}, {'lat':12.23 ,'lng':34.9}] array of dictionaries
        regex = r'''\((?P<lat>[\+\-]?\d+\.\d+)\,\s*(?P<lng>[\+\-]?\d+\.\d+)\)'''
        matcher = re.compile(regex);
        positionArr = [m.groupdict() for m in matcher.finditer(rec['path'])]

        # If current position is null then update vehicle positions to 
        # journey starting point. 
        if(rec['currentPos'] is None):
            db.updateBookedVehiclePos(rec['id'], positionArr[0].get('lat'),
                                      positionArr[0].get('lng'))
            db.updateVehiclePosition(rec['vehicle_id'], positionArr[0].get('lat'), positionArr[0].get('lng'))
        else:

            # print("came to move car")
            a = [float(i) for i in str(rec['currentPos'])[1:][:-1].split(',')]

            b = move1DistanceUnitAlong(positionArr, {'lat':a[0], 'lng':a[1]}, rec['lastIdxOfPath'])
            db.updateBookedVehiclePos(rec['id'], b[0]['lat'], b[0]['lng'],b[1])
            db.updateVehiclePosition(rec['vehicle_id'], b[0]['lat'], b[0]['lng'])

    vehicle_positions = db.getAllVehicles();

    return jsonify(vehicle_positions)

@app.route("/api/reset", methods=['get'])
def reset():
    db.resetDataState();
    vehicles = db.getAllVehicles()
    return jsonify(vehicles)

@app.route("/api/status", methods=['get'])
def status():
    vehicles = db.getAllVehicles()
    return jsonify(vehicles)

@app.route("/api/getBingKey", methods=['get'])
def bingApiKey():
    return jsonify({'key':os.environ['BING_MAPS_API_KEY']})

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
    print(e);
    response = e.get_response()

    response.data = json.dumps({'error':{
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }})
    response.content_type = "application/json"
    return response


    