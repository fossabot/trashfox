#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import make_response
import requests 

app = Flask(__name__)

#Set important global vars
CLIENTID = "aleri"
CLIENTSECRET = "6ec7c884-fd1a-42de-938a-d71b0a84faa0"
USERNAME = "dominik.fehr@aleri.de"
PASSWORD = "elvyEL4pkW8b"
ACCESSTOKEN = ""
SENSORID = "b0038197-cafb-4164-ac8b-8c072b27f4f0"

#Set sensor data @ Com2M
@app.route('/setSensor')
def setSensor():
    print("Trash event received, updating cloud sensor...")
    value = request.args.get('value')
    headers = {'Authorization':ACCESSTOKEN}
    response = requests.post(
        url='https://cloud.com2m.de/api/time-series-service/data-points/values/'+SENSORID,
        json={"capacity":value},
        headers=headers
    ).json()
    return "OK"

#Retrieve latest sensor data from Com2M
@app.route('/getSensor')
def getSensor():
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
        r = requests.post('https://cloud.com2m.de/oauth/token?grant_type=password&username='+USERNAME+'&password='+PASSWORD, auth=(CLIENTID, CLIENTSECRET))
        token =  r.json()['access_token']
        ACCESSTOKEN = "Bearer "+token
        return True
    except:
        print("Failed retrieving access token...")
        return False

#Start main loop by serving an HTTP Server
if __name__ == '__main__':
    print("Starting TrashFox, waiting for trash event...")
    if(loginCom2m()):
        app.run(threaded=True, debug=False, port=8081, host='0.0.0.0')
    else:
        print("Login failed, please check credentials!")
