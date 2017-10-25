#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import make_response
from globals import *
import requests
import json

app = Flask(__name__)

#Set TrashFox sensor ID to be global
def setSensorId(r):
    global SENSORID
    print "Setting sensor id..."
    SENSORID = r['id']

#Check if TrashFox sensor is available
def checkSensor():
    global SENSORID
    print("Checking Sensor...")
    headers = {'Authorization':ACCESSTOKEN}
    r = requests.get(
        url='https://cloud.com2m.de/api/asset-service/items/Device',
        headers=headers
    )
    try:
        if "TrashFox Sensor" in str(r.json()):
            s = str(r.json()['_embedded']['items'])[1:-1]
            s = s.replace("'",'"')
            s = s.replace('u"','"')
            devicedetails = json.loads(s)
            setSensorId(devicedetails)
            print "Sensor "+SENSORID+" found!"
            return True
        else:
            print "Sensor not found..."
            if(addSensor()):
                return True
    except KeyError as e:
        return False

#Add new TrashFox sensor device
def addSensor():
    global SENSORID
    print("Adding new Sensor...")
    headers = {'Authorization':ACCESSTOKEN}
    r = requests.post(
        url='https://cloud.com2m.de/api/asset-service/items/TrashFoxSensor:Device',
        json={'name':'TrashFox Sensor'},
        headers=headers
    ).json()
    setSensorId(r)
    print "Sensor "+SENSORID+" added!"
    return True

#Receive geolocation callback (GET & POST)
@app.route('/geoCallback')
def setGeo():
    global SENSORID
    print("Geolocation callback received, updating cloud values...")
    lng = request.args.get('lng')
    lat = request.args.get('lat')
    station = request.args.get('station')
    rssi = request.args.get('rssi')
    headers = {'Authorization':ACCESSTOKEN}
    response = requests.post(
        url='https://cloud.com2m.de/api/time-series-service/data-points/values/'+SENSORID,
        json={"longitude":lng,"latitude":lat,"station":station,"rssi":rssi},
        headers=headers
    ).json()
    return "OK"

#Set sensor data @ Com2M (GET & POST)
@app.route('/setSensor')
def setSensor():
    global SENSORID
    print("Trash event received, updating cloud sensor...")
    value = request.args.get('value')
    if(int(value)<=100):
        headers = {'Authorization':ACCESSTOKEN}
        response = requests.post(
            url='https://cloud.com2m.de/api/time-series-service/data-points/values/'+SENSORID,
            json={"capacity":value},
            headers=headers
        ).json()
        return "OK"
    else:
        return "ERROR: Invalid value"

#Retrieve latest sensor data from Com2M
@app.route('/getSensor', methods=['GET'])
def getSensor():
    global SENSORID
    print("Trash event received, getting cloud sensor...")
    headers = {'Authorization':ACCESSTOKEN}
    response = requests.get(
        url='https://cloud.com2m.de/api/time-series-service/data-points/values/'+SENSORID+'/latest',
        headers=headers
    ).json()
    return "TrashFox detected a free capacity of "+response['capacity']['value']+"% for this bin. Last update: "+response['capacity']['timestamp']

#Login to Com2M and store OAuth2 access token
def loginCom2m():
    global ACCESSTOKEN
    try:
        print("Trying to log in Com2m...")
        r = requests.post('https://cloud.com2m.de/oauth/token?grant_type=password&username='+USERNAME+'&password='+PASSWORD, auth=(CLIENTID, CLIENTSECRET))
        token =  r.json()['access_token']
        ACCESSTOKEN = "Bearer "+token
        return True
    except:
        print("Failed retrieving access token...")
        return False

#Start main loop by serving an HTTP Server
if __name__ == '__main__':
    global PORT
    print("Starting TrashFox, waiting for trash event...")
    if(loginCom2m()):
        if(checkSensor()):
            app.run(threaded=True, debug=False, port=PORT, host='0.0.0.0')
        else:
            print("Sensor device error, check availability!")
    else:
        print("Login failed, please check credentials!")
