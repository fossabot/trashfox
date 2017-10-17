#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import make_response
import requests 

app = Flask(__name__)

CLIENTID = "aleri"
CLIENTSECRET = "6ec7c884-fd1a-42de-938a-d71b0a84faa0"
USERNAME = "dominik.fehr@aleri.de"
PASSWORD = "elvyEL4pkW8b"
ACCESSTOKEN = ""
SENSORID = "b0038197-cafb-4164-ac8b-8c072b27f4f0"

@app.route('/setSensor')
def setSensor():
    value = request.args.get('value')
    headers = {'Authorization':ACCESSTOKEN}
    response = requests.post(
        url='https://cloud.com2m.de/api/time-series-service/data-points/values/'+SENSORID,
        json={"capacity":value},
        headers=headers
    ).json()
    return "OK"

@app.route('/getSensor')
def getSensor():
    headers = {'Authorization':ACCESSTOKEN}
    response = requests.get(
        url='https://cloud.com2m.de/api/time-series-service/data-points/values/'+SENSORID+'/latest',
        headers=headers
    ).json()
    return "TrashFox detected a free capacity of "+response['capacity']['value']+"% for this bin. Last update: "+response['capacity']['timestamp']

def setupStructure():
    setupBuilding()

def setupBuilding():
    headers = {'Authorization':ACCESSTOKEN}
    response = requests.post(
        url='https://cloud.com2m.de/api/asset-service/items/Building:Group/ad8a51e2-13b4-4e39-8762-f41f847c30d0/members/Sensor:Device',
        json={"name":"TrashSensor"},
        headers=headers
    ).json()
    print headers
    print response

def loginCom2m():
    global ACCESSTOKEN
    try:
        r = requests.post('https://cloud.com2m.de/oauth/token?grant_type=password&username='+USERNAME+'&password='+PASSWORD, auth=(CLIENTID, CLIENTSECRET))
        token =  r.json()['access_token']
        ACCESSTOKEN = "Bearer "+token
        return True
    except:
        print("Failed retrieving access token...")
        return False

if __name__ == '__main__':
    print("Starting TrashFox, waiting for trash event...")
    if(loginCom2m()):
        setupStructure()
        app.run(threaded=True, debug=False, port=8081, host='0.0.0.0')
