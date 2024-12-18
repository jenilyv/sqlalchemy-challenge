# Import the dependencies.
import datetime as dt
import numpy as np
import os

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



# Print current working directory and Python version
print("Current Working Directory:", os.getcwd())
print("Python Version:", os.sys.version)

# Determine the absolute path to the database
# Modify this path as needed based on your actual file location
database_path = os.path.join(os.getcwd(), 'Resources', 'hawaii.sqlite')
print("Database Path:", database_path)

#################################################
# Database Setup
#################################################
# Create engine
try:
    engine = create_engine(f"sqlite:///{database_path}")
    print("Database Engine Created Successfully")
except Exception as e:
    print(f"Error Creating Database Engine: {e}")

# reflect an existing database into a new model
# Reflect the database
try:
    Base = automap_base()
    Base.prepare(autoload_with=engine)
    print("Database Tables Reflected Successfully")
except Exception as e:
    print(f"Error Reflecting Database: {e}")

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
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    session.close()
    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

   # Return the results
    return jsonify(temps=temps)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    try:
        # Create a new session
        session = Session(engine)
        
        # Query stations
        results = session.query(Station.station).all()
        
        # Close the session
        session.close()
        
        # Unravel results and convert to list
        stations_list = list(np.ravel(results))
        
        print("Stations found:", stations_list)
        
        return jsonify(stations=stations_list)
    
    except Exception as e:
        print(f"Error in stations route: {e}")
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)



@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    # Create a new session for this route
    session = Session(engine)
    
    try:
        # Calculate the date 1 year ago from last date in database
        prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

        # Query the primary station for all tobs from the last year
        results = session.query(Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= prev_year).all()
 # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))

        # Return the results
        return jsonify(temps=temps)
    except Exception as e:
        print(f"Error in tobs route: {e}")
        return jsonify(error=str(e)), 500
    finally:
        # Always close the session
        session.close()

if __name__ == '__main__':
    app.run(debug=True)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # start = dt.datetime.strptime(start, "%m/%d/%Y")
        # # calculate TMIN, TAVG, TMAX for dates greater than start
        # results = session.query(*sel).\
        #     filter(Measurement.date >= start).all()
        # # Unravel results into a 1D array and convert to a list
        # temps = list(np.ravel(results))
        # return jsonify(temps)

        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)
    
    # calculate TMIN, TAVG, TMAX with start and stop
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run()