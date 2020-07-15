#!/usr/bin/python3

#imports
import requests
import json
import sys
import smtplib
import ipaddress
from datetime import datetime

now=datetime.now()

#set desired mail server
mailserver='smtp.gmail.com'
port=587
mail=smtplib.SMTP(mailserver,port)
mail.ehlo()
mail.starttls()

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
FW.write('{"logs":{\n')
num=1
#Log information and check information 
for i in okta[:-1]:
	try:
		info='"event'+str(num)+'":{"user":"'+i['actor']['displayName']+'","email_address":"'+i['actor']['alternateId']+'","ip_address":"'+i['client']['ipAddress']+'","state":"'+i['client']['geographicalContext']['state']+'","country":"'+i['client']['geographicalContext']['country']+'","outcome":"'+i['outcome']['result']+'","date":"'+i['published']+'"},\n'
		FW.write(info)
		#Check for logins outside of the US
		if(i['client']['geographicalContext']['country']!="United States"):
			print("ERR: Overseas login detected. Emailing Alert\n")
			mail.ehlo()
			mail.login(address.strip(), password.strip())
			header = 'To: '+to+ '\n From: '+address+'\n Subject: OKTA ALERT: OVERSEA LOGIN\n'
			msg=header+info
			mail.sendmail(address,to,msg)
		#Check for blackisted network logins
		BL=open('../sec/blacklisted-networks',)
		ip=ipaddress.ip_address(i['client']['ipAddress'])	
		for entry in BL:
			network=ipaddress.ip_network(entry.strip())
			for ipv4address in network:
				if(ipv4address == ip):
					print("ERR: Suspicious IP address used in login. Emailing Alert\n")
					mail.ehlo()
					mail.login(address.strip(), password.strip())
					header = 'To: '+to+ '\n From: '+address+'\n Subject: OKTA ALERT: BAD IP\n'
					msg=header+info
					mail.sendmail(address,to,msg)
		BL.close()
	except:
		print("Err: Invalid formatting on Event Log number "+str(num)+". This is not fatal. Information provided below: \n", sys.exc_info()[0])
		continue
	num=num+1
else:
	info='"event'+str(num)+'":{"user":"'+i['actor']['displayName']+'","email_address":"'+i['actor']['alternateId']+'","ip_address":"'+i['client']['ipAddress']+'","state":"'+i['client']['geographicalContext']['state']+'","country":"'+i['client']['geographicalContext']['country']+'","outcome":"'+i['outcome']['result']+'","date":"'+i['published']+'"}\n'
	#Check for logins outside of the US
	if(i['client']['geographicalContext']['country']!="United States"):
		print("ERR: Overseas login detected. Emailing Alert\n")
		mail.ehlo()
		mail.starttls()
		mail.login(address.strip(), password.strip())
		header = 'To: '+to+ '\n From: '+address+'\n Subject: OKTA ALERT: OVERSEA LOGIN\n'
		msg=header+info
		mail.sendmail(address,to,msg)
	#Check for blackisted network logins
	BL=open('../sec/blacklisted-networks',)
	ip=ipaddress.ip_address(i['client']['ipAddress'])
	for entry in BL:
		network=ipaddress.ip_network(entry.strip())
		for ipv4address in network:
			if(ipv4address == ip):
				print("ERR: Suspicious IP address used in login. Emailing Alert\n")
				mail.ehlo()
				mail.login(address.strip(), password.strip())
				header = 'To: '+to+ '\n From: '+address+'\n Subject: OKTA ALERT: BAD IP\n'
				msg=header+info
				mail.sendmail(address,to,msg)
	BL.close()
	FW.write(info) 
FW.write("}}")

#Email notification
mail.ehlo()
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