import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API! by Diana Chacon<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Find the max date using SQLAlchemy
    rec_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # Change format - split date
    tmp = rec_date.split("-")
    date = [int(x) for x in tmp]
    # Calculate the date 1 year ago from last date in database
    year_ago = dt.date(*date) - dt.timedelta(days=365)
    
    # Query for the date and precipitation for the last year
    year_prec = session.query(Measurement.date.label('Measurement Date'), Measurement.prcp.label('Measurement Precipitation')).\
        filter(Measurement.date > year_ago).\
        order_by(Measurement.date.asc()).all()
    
    # Dict with 'Measurement Date'as the key and 'Measurement Precipitation' as the value
    date_prec = list(np.ravel(year_prec))
    return jsonify(date_prec)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    list_stations = session.query(Station.station).all()
    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(list_stations))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Find the max date using SQLAlchemy (recent date)
    rec_date = session.query(Measurement.date).order_by(Measurement.date.desc()).filter(Measurement.station=='USC00519281').first()
    rec_date
    """Return the temperature observations (tobs) for previous year."""
    
    # Query the primary station for all tobs from the last year
    year_tobs = session.query(Measurement.date, Measurement.tobs.label('Measurement Temperature')).\
        filter(Measurement.date > '2016-08-18').filter(Measurement.station=='USC00519281').all()

    
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(year_tobs))
    # Return the results
    return jsonify(temps)


@app.route("/api/v1.0/temp/<start>/<end>")

def calc_temps(start_date, end_date):
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Use your previous function `calc_temps` to calculate the tmin, tavg, and tmax 
    # for your trip using the previous year's data for those same dates.

    my_trip_temps = calc_temps('2017-01-01', '2017-01-07')[0]

     # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(my_trip_temps))
    # Return the results
    return jsonify(temps) 

if __name__ == '__main__':
    app.run()