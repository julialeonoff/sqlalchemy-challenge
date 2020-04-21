# Declaration of Depedencies
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect databse into new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Fill the Flask
app = Flask(__name__)

# Plan some routes with da flask
# Homepage
@app.route("/")
def homepage():
    return (
        f"Welcome! <br/>"
        f"Looking to vacation in Hawaii? B/c same :( <br/>"
        f"Checkout these Available Routes so we can see what we're missing out on together: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start <br/>"
        f"/api/v1.0/start/end"
    )

# Precipitaton 
# (assuming that "convert query results" means use same dates as OG query?)
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    #Find dates so we can have same results as og query
    latest_date = session.query(Measurement.date)\
                    .order_by(Measurement.date.desc()).first()
    latest_date = (dt.datetime.strptime(latest_date[0], '%Y-%m-%d'))
    year_ago = (latest_date - dt.timedelta(days=365)).strftime('%Y-%m-%d')
  
    # QueryQueryQuery
    results = session.query(Measurement.date, Measurement.prcp)\
                .filter(Measurement.date >= year_ago).all()

    session.close()

    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_data.append(prcp_dict)
    
    return jsonify(prcp_data)

# Stations 
# (kinda unclear on what info is wanted from stations, so hope this is enough and rip me if not :o )
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()

    session.close()

    station_list = list(np.ravel(results))

    return jsonify(station_list)

# Temperature 
# (also p unclear on this one, does previous year = last year of data? hope so)
# (also hope you only want temperatures returned as the list, unsure if instructions implied we should also get the date)
@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)

    # Find dates again woooo
    latest_date = session.query(Measurement.date)\
                    .order_by(Measurement.date.desc()).first()
    latest_date = (dt.datetime.strptime(latest_date[0], '%Y-%m-%d'))
    year_ago = (latest_date - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    #QueryQueryQuery
    results = session.query(Measurement.tobs)\
                .filter(Measurement.date >= year_ago)\
                .filter(Measurement.station == "USC00519281").all()

    session.close()

    temp_list = list(np.ravel(results))

    return jsonify(temp_list)

# Start
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), 
                            func.max(Measurement.tobs), 
                            func.avg(Measurement.tobs))\
                .filter(Measurement.date >= start).all()   
    session.close()

    data = []
    for min, max, avg in results:
        data_dict = {}
        data_dict["Min"] = min
        data_dict["Max"] = max
        data_dict["Avg"] = avg
        data.append(data_dict)
    
    return jsonify(data)

# Start-End
@app.route("/api/v1.0/<start>/<end>")
def dates(start, end):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), 
                            func.max(Measurement.tobs), 
                            func.avg(Measurement.tobs))\
                .filter(Measurement.date >= start)\
                .filter(Measurement.date <= end).all()   
    session.close()

    data = []
    for min, max, avg in results:
        data_dict = {}
        data_dict["Min"] = min
        data_dict["Max"] = max
        data_dict["Avg"] = avg
        data.append(data_dict)
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)