#!/usr/bin/python3

#imports
import requests
import json
import sys
import smtplib
from datetime import datetime

now=datetime.now()

#set desired mail server
mailserver='smtp.gmail.com'
port=587
mail=smtplib.SMTP(mailserver,port)

#get email address
FP=open('../sec/email-address', 'r')
address=FP.readline()
to="anthony@italianoaj.com"
FP.close()

#get email password
FP=open('../sec/email-password', 'r')
password=FP.readline()
FP.close()

#get API token
FP=open('../sec/api-tok-okta', 'r')
token=FP.readline()
FP.close()

#Print Token(logs)
print(token)
print(now)

#Open log file
FP=open('../sec/okta.json', 'w+')

#Make API request
url = "https://stratos.okta.com/api/v1/logs"
payload = ""
head={'Content-Type':'application/json',
	'Accept':'application/json',
	'Authorization':'SSWS '+token.strip()
	}

req=requests.request("GET", url, data=payload, headers=head)

#Store logs in log file
print(req.text, file=FP)
FP.close()

#Parse out uneeded log information
FP=open('../sec/okta.json',)
FW=open('../sec/parsed_okta.json', 'w')
okta = json.loads(FP.read())

for i in okta:
	try:
		info='"event":{"user":"'+i['actor']['displayName']+'","email_address":"'+i['actor']['alternateId']+'","ip_address":"'+i['client']['ipAddress']+'","state":"'+i['client']['geographicalContext']['state']+'","country":"'+i['client']['geographicalContext']['country']+'","outcome":"'+i['outcome']['result']+'","date":"'+i['published']+'"}\n'
		FW.write(info)
	except:
		continue

#Email notification
mail.ehlo()
mail.starttls()
mail.login(address.strip(), password.strip())
header = 'To: ' +to+ '\n' + 'From: ' +address+ '\n' + 'Subject:Okta Logs Recorded\n'
msg=header+"\n Logs have been successfully placed at /home/italianoaj/projects/sec/parsed_okta.json"
mail.sendmail(address,to,msg)

#Close mail service
mail.close()

#Close Log File
FP.close()
FW.close()

#Exit program
sys.exit()