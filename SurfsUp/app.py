# Import the dependencies.
from flask import Flask, jsonify, redirect
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

import os

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)



#################################################
# Flask Setup
#################################################
app = Flask(__name__)

def date_prior_year():
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    first_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    return(first_date)



#################################################
# Flask Routes
#################################################
@app.route('/')
def homepage():
    return(
        f"<h1>Welcome to the Hawaii Climate Page!<h1><br/>"
        f"<h2>Available Routes:<h2><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(2016-09-06)<br/>"
        f"/api/v1.0/(2015-12-25_2017-01-01)")

#Create a route that queries precipitation levels and dates 
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_prior_year()).all()

#Create an empty list of precipitation query    
    prcp_list = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)
session.close()

#Create a route for the stations 
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_data = session.query(Station.station).all()

    station_list = list(np.ravel(station_data))

    return jsonify(station_list)
session.close()

#Create a route that queries date and temp observed for most active stations
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= date_prior_year()).all()

    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)
session.close()

#Create a route 
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
#def start_date(start):
def cal_temp(start=None, end=None):
    session = Session(engine)
    sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_data = session.query(*sel).\
        filter(Measurement.date >= start).all()
    start_list = []
    for min, avg, max in start_data:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["average"] = avg
        start_date_tobs_dict["max"] = max
        start_list.append(start_date_tobs_dict)

    if end == None:
        start_data = session.query(*sel).\
        filter(Measurement.date >= start).all()
        start_list = list(np.ravel(start_data))
        
        return jsonify(start_list)
    else:
        start_end_data = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
        start_end_list = list(np.ravel(start_end_data))

        return jsonify(start_end_list)
session.close()
    # if __name__ == "__main__":
    #     app.run(degug = True)
# @app.route("/api/v1.0/<start>/<end>")
# def start_end_date(start, end):
#     sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
#     start_end_data = session.query(*sel).\
#         filter(Measurement.date >= start).\
#         filter(Measurement.date <= end).all()

#     start_end_tobs_date = []
#     for min, avg, max in start_end_data:
#         start_end_tobs_date_dict = {}
#         start_end_tobs_date_dict["min_temp"] = min
#         start_end_tobs_date_dict["avg_temp"] = avg
#         start_end_tobs_date_dict["max_temp"] = max
#         start_end_date.append(start_end_tobs_date_dict)

    #return jsonify(start_end_tobs_date)
    #last_year_data = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date)


# @app.route('/people')
# def people():
#     resp = '<ul>'
#     for p in ppl:
#         resp += f'<li>{p}</li>'
#     resp += '</ul>'     
#     return resp  

# @app.route('/add/<name>')
# def add(name):
#     ppl.append(name)
#     return redirect('/people')

# @app.route('/stations')
# def stations():
#     station_count = session.query(func.count(Station.station)).scalar()
#     return f'<h2>Station Count: {station_count}</h2>'



    #print("Server received request for 'Home' page...")
    #return "Welcome to Hawaii Climate Zone!"

#for rule in app.url_map.iter_rules():
    #print (rule)

# @app.route('/api/v1.0/precipitation')
# def precipitation():
#     session = Session(engine)
#     first_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
#     precipitation = session.query(Measurment.date, Measurement.prcp).filter(Measurment.date >= first_date)
    
app.run()
session.close()