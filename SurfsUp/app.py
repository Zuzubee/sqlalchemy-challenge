# Import the dependencies.
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm         import Session
from sqlalchemy             import create_engine, func
from flask                  import Flask, jsonify

import datetime as dt
import sqlalchemy

# Python SQL toolkit and Object Relational Mapper 
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station     = Base.classes.station

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
            "/api/v1.0/Stations : Stations from the data <br/>"
            "/api/v1.0/tobs : list dates and tobs from an year for the last data point (2017-08-23) <br/>"
            "/api/v1.0/startdate : show min, avg, and max temperature for a specified start date <br/>"
            "/api/v1.0/startdate/enddate : show min, avg, and max temperature for a specified start and end date <br/><br/>")


# 2. Convert the query results from your precipitation analysis using date as the key and prcp as the value..
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    dict_prcp = dict(prcp_data)
    
    session.close()
    
    # return a JSONified dict
    return jsonify(dict_prcp)

# 3. Return a JSON list of Stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    
    session  = Session(engine)
    
    stations_tuple = session.query(Station.station).all()
    session.close()
    
    stations_list = list(np.ravel(stations_tuple))
    
    # return a JSONified Stations List
    return jsonify(stations_list)

# 4. Query the dates and temperature observations of the most-active Station for the previous year of data.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    latest_date = dt.date(2017,8, 23)
    
    year_ago = latest_date - dt.timedelta(days=365)
    year_ago = (year_ago.strftime("%Y-%m-%d"))
    
    last_12 = session.query(Measurement.date, Measurement.tobs).filter_by(station = "USC00519281").\
    filter(Measurement.date >= year_ago).all()
    
    session.close()
    
    last_12_list = []
    for date, tobs in last_12:
        tobs_dict       = {}
        tobs_dict[date] = tobs
        last_12_list.append(tobs_dict)
    
    # return a JSONified tobs
    return jsonify(last_12_list)


# 5. For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    session = Session(engine)
    
    temperature = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
                                func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    session.close()
    
    temp_list = []
    for i in temperature:
        temp_dict = {}
        
        temp_dict['Date'] = i[0]
        temp_dict['TMIN'] = i[1]
        temp_dict['TAVG'] = round(i[2], 1)
        temp_dict['TMAX'] = i[3]
        
        temp_list.append(temp_dict)
    
    # return a JSON list
    return jsonify(temp_list)
        
# 6. For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    
    temperature = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
                                func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <=
                                                                                                     end).group_by(Measurement.date).all()
    session.close()
    
    temp_list = []
    for i in temperature:
        temp_dict = {}
    
        temp_dict['Date'] = i[0]
        temp_dict['TMIN'] = i[1]
        temp_dict['TAVG'] = round(i[2], 1)
        temp_dict['TMAX'] = i[3]
        
        temp_list.append(temp_dict)
    
    # return a JSON List 
    return jsonify(temp_list)


if __name__ == '__main__':
    app.run(debug=True)
