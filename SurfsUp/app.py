# Import the dependencies.
from datetime               import datetime, timedelta
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm         import Session
from sqlalchemy             import create_engine, func
from flask                  import Flask, jsonify

import sqlalchemy

# Python SQL toolkit and Object Relational Mapper 
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(engine, reflect=True)

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# 1. Homepage. List all the available routes.
@app.route('/')
def homepage():
    return ("All routes <br/>"
            "/api/v1.0/precipitation : dates and precipitation route <br/>"
            "/api/v1.0/stations : stations from the data <br/>"
            "/api/v1.0/tobs : list dates and tobs from an year for the last data point (2017-08-23) <br/>"
            "/api/v1.0/startdate : show min, avg, and max temperature for a specified start date <br/>"
            "/api/v1.0/startdate/enddate : show min, avg, and max temperature for a specified start and end date <br/><br/>")


# 2. Convert the query results from your precipitation analysis using date as the key and prcp as the value..
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    year_ago = datetime(2017, 8, 23) - timedelta(days=365)
    prcp_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).all()
    dict_prcp = dict(prcp_data)
    session.close()
    
    # return a JSONified dict
    return jsonify(dict_prcp)

# 3. Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session  = Session(engine)
    stations = session.query(stations.station).all()
    session.close()
    
    # return a JSONified stations
    return jsonify(stations)

# 4. Query the dates and temperature observations of the most-active station for the previous year of data.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    year, month, day = map(int, last_date.split('-'))
    year_ago = datetime(year, month, day) - timedelta(days=365)
    year_ago = (year_ago.strftime("%Y-%m-%d"))
    
    tobs = session.query(measurement.date, measurement.tobs).filter(measurement.date >= year_ago).all()
    session.close()
    
    # return a JSONified tobs
    return jsonify(tobs)
    
# 5. For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    
    temperature = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs),
                                func.max(measurement.tobs)).filter(measurement.date >= start).groupby(measurement.date).all()
    session.close()
    
    for i in temperature:
        temp_dict = {}
        
        temp_dict['Date'] = i[0]
        temp_dict['TMIN'] = i[1]
        temp_dict['TAVG'] = i[2]
        temp_dict['TMAX'] = i[3]
        
        temp_list = []
        
        temp_list.append(temp_dict)
    
    # return a JSON list
    return jsonify(temp_list)
        
# 6. For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    
    temperature = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs),
                                func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <=
                                                                                                     end).groupby(measurement.date).all()
    session.close()
    
    for i in temperature:
        temp_dict = {}
        
        temp_dict['Date'] = i[0]
        temp_dict['TMIN'] = i[1]
        temp_dict['TAVG'] = i[2]
        temp_dict['TMAX'] = i[3]
        
        temp_list = []
        temp_list.append(temp_dict)
    
    # return a JSON list
    return jsonify(temp_list)



if __name__ == '__main__':
    app.run(debug=True)
