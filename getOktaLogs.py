#!/usr/bin/python3

import requests
import json

FP=open('../sec/api-tok-okta', 'r')
token=FP.readline()
FP.close()

print(token)

FP=open('/logs/test.log', 'w')

url = "https://[DOMAIN].okta.com/api/v1/logs"
payload = ""
head={'Content-Type':'application/json',
	'Accept':'application/json',
	'Authorization':'SSWS '+token.strip()
	}

req=requests.request("GET", url, data=payload, headers=head)

print(req.text, file=FP)
FP.close()

