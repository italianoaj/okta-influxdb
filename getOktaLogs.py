#!/usr/bin/python3

import requests
import json

FP=open('logs/test.log', 'w')

tok = '******************************************'
url = "https://[DOMAIN].okta.com/api/v1/logs"
payload = ""
head={'Content-Type':'application/json',
	'Accept':'application/json',
	'Authorization':'SSWS '+tok+'
	}

req=requests.request("GET", url, data=payload, headers=head)

print(req.text, file=FP)
FP.close()

