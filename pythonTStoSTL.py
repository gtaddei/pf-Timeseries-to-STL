import requests
import json
import pandas as pd
import os
from solid import *
from solid.utils import *
from subprocess import Popen

CLIENT_SECRET = "*Your Base64 Encoded ClientID:ClientSecret*"
CLIENT_TOKEN = "none"
UAA_URI = "https://*your-uaa*.predix-uaa.run.aws-usw02-pr.ice.predix.io"
GET_TS_URL = "https://time-series-store-predix.run.aws-usw02-pr.ice.predix.io/v1/datapoints/"
TIMESERIES_ZONE_ID = "your timeseries zone id"
START_TIME='*how long ago*-ago' #50y-ago if you want to print all you timeseries
payload_last = "{\n  \"start\": \"" + START_TIME + "\",\n  \"tags\": [\n    {\n      \"name\": \"String\",\n      \"order\": \"desc\",\n      \"limit\": 1\n    }\n  ]\n}"
payload_first = "{\n  \"start\": \"" + START_TIME + "\",\n  \"tags\": [\n    {\n      \"name\": \"String\",\n      \"order\": \"asc\",\n      \"limit\": 1\n    }\n  ]\n}"

def connectUAA():
    url = UAA_URI + "/oauth/token"
    authorization = "Basic " + CLIENT_SECRET
    headers = {
        'Authorization': authorization,
        'Content-Type': "application/x-www-form-urlencoded",
    }
    payload = dict(grant_type="client_credentials")
    r = requests.post(url, headers=headers, data=payload)
    response = r.text
    return response.split(":")[1].split('"')[1]

def queryTS(payload):
    url = GET_TS_URL
    authorization = "Basic " + CLIENT_SECRET
    headers = {
        'Authorization': "Bearer " + CLIENT_TOKEN,
        'Content-Type': "application/json",
        'predix-zone-id': "" + TIMESERIES_ZONE_ID
    }
    response = requests.post(url, headers=headers, data=payload)
    data = json.loads(response.text)['tags'][0]['results'][0]['values']
    return data


CLIENT_TOKEN = connectUAA()

firstPoint = queryTS(payload_first)
startDate =  firstPoint[0][0]
startDate = int(startDate)

lastPoint = queryTS(payload_last)
endDate =  lastPoint[0][0]
endDate = int(endDate)
arrayColor = [Red, Blue, Green, Cyan, Magenta, Yellow, Oak, Pine, Birch, Iron, Steel, Stainless, Aluminum, Brass, BlackPaint, FiberBoard]
pdArray = []
j = 0
maxVal = 0

while(startDate < endDate):
    payload = {'cache_time': 0, 'tags': [{'name': 'String','order': 'asc'}], 'start': startDate, 'end': startDate + 10000000}
    startDate = startDate + 10000000
    data = queryTS(json.dumps(payload))
    nb_elem = len(data)
    if(nb_elem > 0):
        curr = data[0][0]
        i = 0
        while i < nb_elem:
            nb = 0
            while(data[i][0] < curr + 1000000 and i < nb_elem - 1):
                nb = nb + 1
                i += 1
            pdArray.append([curr, nb, 3])
            if maxVal < nb:
                maxVal = nb
            bar = color(arrayColor[j%len(arrayColor)])(right(10*j + 10)(up(5)(cube([5, 5, nb]))))
            if j == 0:
                scad = bar
            else:
                scad = scad + bar
            curr = data[i-1][0]
            i += 1
            j += 1
            print nb
print pdArray

scad = scad + back(6)(left(6)(up(maxVal + 20)(cube([16,16,5])))) + cube([5, 5, maxVal + 20]) + back(5)(cube([len(pdArray)*10 + 10, 15, 5])) + back(15)(cube([5, 30, 5])) + back(15)(right(len(pdArray)*10 + 10)(cube([5, 30, 5])))

f = open('output.scad', 'w')
f.write(scad_render(scad) + '\n')
f.close()

Popen(['openscad', '-o', 'output.stl', 'output.scad'])
