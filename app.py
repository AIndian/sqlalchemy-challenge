import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#reflectthe database
Base = automap_base()
Base.prepare(engine,reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station


#FLASK
app = Flask(__name__)

#Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/tempdate<start><br/>"
        f"/api/v1.0/tempdaterange/<start>/<end><br/>"  
        )

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    all_stations = []
    results = session.query(Station.station, Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()
    for x,name,la,li,ele in results:
        stations = {}
        stations["id"]=x
        stations["name"]=name
        stations["elevation"]=ele
        stations["latitude"]= la
        stations["longitude"]=li
        all_stations.append(stations)
    return jsonify(all_stations)

@app.route("/api/v1.0/precipitation")
def precipitation():
    precip= {}
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    for x,prcp in results:
        precip[x] = prcp
    return jsonify(precip)

@app.route("/api/v1.0/tobs")
def tobs():
    tobs = []
    session = Session(engine)
    active = session.query(Measurement.station,func.count(Measurement.id)).\
        group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()
    mostactiveid = active[0][0]
    datef = session.query(func.max(Measurement.date)).filter(Measurement.station == mostactiveid).all()
    datefirst = dt.datetime.strptime(datef[0][0],'%Y-%m-%d')
    datelast =dt.date(datefirst.year - 1,datefirst.month,datefirst.day)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == mostactiveid).filter(Measurement.date > datelast).all()
    session.close()
    for x,tp in results:
        temps=      {}
        temps["date"] = x
        temps["temperature"]=tp
        tobs.append(temps)
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def tempstart(start):
    temstart = []
    session=Session(engine)
    results = session.query(Measurement.date,func.min(Measurement.tobs),func.avg(Measurement.tobs)\
        ,func.max(Measurement.tobs))\
        .filter(Measurement.date>=start)\
        .group_by(Measurement.date).all()
    session.close()
    for date,min,avg,max in results:
        temp= {}
        temp["Date"] = date
        temp["TMIN"] = min
        temp["TAVG"] = avg
        temp["TMAX"] = max
        temstart.append(temp)
    return jsonify(temstart)

@app.route("/api/v1.0/<start>/<end>")
def tempstartend(start,end):
    temstart = []
    session=Session(engine)
    results = session.query(Measurement.date,func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs))\
         .filter(Measurement.date>=start).filter(Measurement.date<= end)\
         .group_by(Measurement.date).all()
    session.close()
    for date,min,avg,max in results:
        temp= {}
        temp["Date"] = date
        temp["TMIN"] = min
        temp["TAVG"] = avg
        temp["TMAX"] = max
        temstart.append(temp)
    return jsonify(temstart)


if __name__ == '__main__':
    app.run(debug = True, use_reloader = False)
    