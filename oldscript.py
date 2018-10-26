# Developed by Elim Garak with funding from Setec Astronomy 2017
# Environment used: Python 3.4, Sublime text, Vim, iPython. 


# This script is used to parse kippo log files for ICTN4800 course at ECU.

#
#
#
#

# For great books on Python, check out NoStarch Press. For some awesome courses, check out Coursera's 'python for everybody' with charles severance  
# Green Tea Press't 'think python', the second edition, is also a good read. http://greenteapress.com/wp/think-python-2e/  

# You will need to download the maxmind database and update the file location in this script. 
# This can be found here https://dev.maxmind.com/geoip/geoip2/geolite2/   
# Use the database, not the CSV file.



# Sample log file https://pastebin.com/R62yaBvd
# If your a student in ICTN4800, It's easier to download the kippo.log file from the host instead of using the kippo update script provided to you. I used PSCP to do such. 

#rewrite template needed soon: https://pastebin.com/em8srXMe  

# you will need to pip install geoip2 - http://geoip2.readthedocs.io/en/latest/  

'''
 output csv file issues with automatic formating and data type conversion 
	see: https://stackoverflow.com/questions/7691485/how-to-globally-stop-excel-date-autoformatting
	see: https://docs.python.org/3.4/library/csv.html
'''
# Have questions? Reach out to me. 


#global declarations 


import sys, csv, re, time, io
from collections import Counter
from pprint import pprint

try:
	import geoip2, geoip2.database
except ImportError:
	print("You need to pip install geoip2.")
	time.sleep(5.0)
	sys.exit("No geoip2") 

try:
	import requests
except ImportError:
	print("You need to pip install requests.")
	time.sleep(5.0)
	sys.exit("No requests module installed")


start = time.time()
linecount, uniqueIPcounter, failed_counter, succeeded_counter, api_counter, skipped_apicall, unique_pass_count, pass_counter = 0, 0, 0, 0, 0, 0, 0, 0
set_of_ip = set()
greyres_capture_data = dict()
pass_counter_dict = dict()
country_counter = Counter()



def country_counter_function(foundGEO):
	country_counter[foundGEO] +=1




# This gets things started
def startmeup():
    print("\n\n\nTo verify yourself please repeat the following - Hi, my name is Werner Brandes. My voice is my passport. Verify Me.")
    time.sleep(7.6)
    print("LISTENING, please speak louder!")
    time.sleep(8.3)
    print("Thank you! Verification complete.")
    input("Press enter to continue")

# This gets the country name via maxmind database and geoip2. You will need to pip install and download the local db. 
def getcountryname(foundIP):
    response = reader.country(foundIP)
    return response.country.name


#this builds a set of unique ip addresses
def uniqueIP(foundIP):     
    if (foundIP) in set_of_ip:
        return 
    else:
        set_of_ip.add(foundIP)
        global uniqueIPcounter 
        uniqueIPcounter += 1
        

#greynoise API lookup function 
#key: field1, field2, field3
#IP: greyres_name, greyres_intention, greyres_os
#192.168.1.1: SSHSCANNER, Malicious, WIndowsXP
# The first if statement checks to see if the entry already exists in the dictionary to prevent duplicate api calls. 
def greynoise(greyIP):
    if greyIP in greyres_capture_data:
        greyres_name = greyres_capture_data[greyIP][0] 
        greyres_intention = greyres_capture_data[greyIP][1] 
        greyres_os = greyres_capture_data[greyIP][2] 
        global skipped_apicall
        skipped_apicall += 1
        print("skipped api call is : ", skipped_apicall, "\n\n")  #for debuging 
    else:
        global api_counter
        api_counter += 1
        print("api call counter is: ", api_counter)
        greyres = requests.post('http://api.greynoise.io:8888/v1/query/ip', data={'ip': greyIP})
        greyres_dict = greyres.json()
        greyres_status = greyres_dict["status"]
        if "ok" == greyres_status:    #if greyres status field is ok, then a record exists. It it doesnt, jump to else and fill lines with none. 
            greyres_name = greyres_dict["records"][0]['name']
            greyres_intention = greyres_dict["records"][0]["intention"]
            if not greyres_intention:
            	greyres_intention = "None"
            greyres_os = greyres_dict['records'][0]['metadata']['os']
            greyres_capture_data[greyIP] = [greyres_name, greyres_intention, greyres_os]
            print(greyres_name, greyres_intention, greyres_os)
        else:
            print(greyres_status, greyIP)  #testing found that ip 200.145.23.13 returned status "unknown" which i believe to be the default status for nothing found
            greyres_name, greyres_intention, greyres_os = "None", "None", "None"
            greyres_capture_data[greyIP] = [greyres_name, greyres_intention, greyres_os]
    print(greyres_capture_data)
    return greyres_name, greyres_intention, greyres_os


#function to count unique passwords 
def password_counter(foundpass):
    global pass_counter
    pass_counter +=1   
    if foundpass in pass_counter_dict:
        pass_counter_dict[foundpass] += 1
    else:
        pass_counter_dict[foundpass] = 1
        global unique_pass_count
        unique_pass_count +=1
    print(pass_counter_dict[foundpass])
    print("The total UNIQUE password count is ", unique_pass_count)
    print("The total password attempts count is ", pass_counter)

def printstats():
    print("\n\n")
    print(" the length of set_of_ip, set of all unique ip's, is: ", len(set_of_ip))
    print(" Log file total lines processed: ", linecount, ".\n The total unique IP count is: ", uniqueIPcounter, ".\n Total succeeded logins was: ", succeeded_counter, ".\n Total failed logins was: ", failed_counter, ". \n")
    print(" The total api calls was: ", api_counter, "!")
    print(" The total skipped api calls was: ", skipped_apicall, "!")
    print(" The total unique IP's: ", uniqueIPcounter, "  and total api_counter: ", api_counter, " should match. \n\n")
    print(" The total unique passwords attempted was: ", unique_pass_count)
    print("\n\n")
    top10pass()
    print("the top countries are:  ", (country_counter.most_common(5)))
    print(' Running this script took {0:0.1f} seconds'.format(time.time() - start))
    print(' Running this script took {0:0.1f} minutes'.format((time.time() - start) / 60))
    input("Press enter to exit ;)")

#This function prints the top 15 passwords and how often they were used
def top10pass():
    length_of_pass_counter_dict = len(pass_counter_dict)
    top10slice = length_of_pass_counter_dict - 15
    sorted_pass_counter_dict = sorted(pass_counter_dict.items(), key = lambda x: x[1])
    print("Here comes the top 15 passwords: \n")
    pprint(sorted_pass_counter_dict[top10slice:])


reader = geoip2.database.Reader('C:/Users/Home/Documents/homework/ECU/ICTN 4800/kippo stuff/final lab/FHHTTP/GeoLite2-Country.mmdb')
startmeup()
with open('C:/Users/Home/Documents/homework/ECU/ICTN 4800/kippo stuff/final lab/kippo/kippo.log', 'r') as f:
    with open('oldkippo4final.csv', 'w', newline = '') as output:
        writer = csv.writer(output)
        for line in f:
            foundLogins = re.search(r'attempt\s\[([^]]+)\/(.+?)\]\s', line)
            if foundLogins is not None:
                foundLogins.group(1), foundLogins.group(2)
                #print("the linecount is ", linecount)
                linecount += 1  # for error checking
                foundIP = re.search(r',(\d{1,}\.\d{1,}\.\d{1,}\.\d{1,})\]\sl', line)
                foundGEO = getcountryname(foundIP.group(1))
                country_counter_function(foundGEO)
                foundpass = (foundLogins.group(2))
                password_counter(foundpass)
                if re.search(r'failed', line):
                    state = "failed"
                    failed_counter += 1
                else: 
                    state = "succeeded"
                    succeeded_counter +=1
                uniqueIP(foundIP.group(1))
                greyIP = (foundIP.group(1))
                greyres_name, greyres_intention, greyres_os = greynoise(greyIP)
                writer.writerow([foundGEO, foundIP.group(1), foundLogins.group(1), foundLogins.group(2), state, greyres_name, greyres_intention, greyres_os])
printstats()

#printing log stats and time it took to process

'''
def printstats():
    print("\n\n")
    print(" the length of set_of_ip, set of all unique ip's, is: ", len(set_of_ip))
    print(" Log file total lines processed: ", linecount, ".\n The total unique IP count is: ", uniqueIPcounter, ".\n Total succeeded logins was: ", succeeded_counter, ".\n Total failed logins was: ", failed_counter, ". \n")
    print(" The total api calls was: ", api_counter, "!")
    print(" The total skipped api calls was: ", skipped_apicall, "!")
    print(" The total unique IP's: ", uniqueIPcounter, "  and total api_counter: ", api_counter, " should match. \n\n")
    print(" The total unique passwords attempted was: ", unique_pass_count)
    print("\n\n")
    top10pass()
    print('varable start is: ', start)
    print("testing this ", time.time() - start)
    print("testing this ", (time.time() - start))
    print(time.time() - start / 60)
    print((time.time() - start) / 60)
    print(' Running this script took {0:0.1f} seconds'.format(time.time() - start))
    print(' Running this script took {0:0.1f} minutes'.format((time.time() - start) / 60))
    print(' Running this script took: ', (time.time() - start).total_seconds() / 60, " minutes.")
    input("Press enter to exit ;)")
    #print(set_of_ip)  #this works, removing 


'''





# regex for ip's 
#    ,(\d{1,}\.\d{1,}\.\d{1,}\.\d{1,})\]\sl
     
        # had this list stuff but we dont need it - recordsList.extend([foundGeo, foundIP, foundFile])
        #print(recordsList)
        
        #python go|dfish  you can place file paths into variable to shorten the code a bit
        #you can use  open(..) as f, open(...) as output: to shorten also

'''
more error checking removed
print(len(recordsList))
print(recordsList[0:10])
print("bye")
'''

''' 
notes for the future
>>> test = requests.post('http://api.greynoise.io:8888/v1/query/ip', "ip=193.201.224.109")
>>> test.text
'{"ip":"","status":"unknown"}'
>>> test = requests.post('http://api.greynoise.io:8888/v1/query/ip', data={'ip': '193.201.224.109'})
>>> test.text
'{"ip":"193.201.224.109","status":"ok","returned_count":2,"records":[{"name":"SSH_SCANNER_LOW","first_seen":"2017-11-13T20:02:11.444Z","last_updated":"2017-11-14T15:09:02.251Z","confidence":"low","intention":"","category":"activity","metadata":{"org":"PE Tetyana Mysyk","rdns":"","rdns_parent":"","datacenter":"ProHoster.info","asn":"AS25092","os":"","link":"","tor":false}},{"name":"SSH_WORM_HIGH","first_seen":"2017-11-13T19:49:24.459Z","last_updated":"2017-11-14T14:55:02.467Z","confidence":"high","intention":"malicious","category":"worm","metadata":{"org":"PE Tetyana Mysyk","rdns":"","rdns_parent":"","datacenter":"ProHoster.info","asn":"AS25092","os":"","link":"","tor":false}}]}'
>>> test.json()
{'ip': '193.201.224.109', 'status': 'ok', 'returned_count': 2, 'records': [{'name': 'SSH_SCANNER_LOW', 'first_seen': '2017-11-13T20:02:11.444Z', 'last_updated': '2017-11-14T15:09:02.251Z', 'confidence': 'low', 'intention': '', 'category': 'activity', 'metadata': {'org': 'PE Tetyana Mysyk', 'rdns': '', 'rdns_parent': '', 'datacenter': 'ProHoster.info', 'asn': 'AS25092', 'os': '', 'link': '', 'tor': False}}, {'name': 'SSH_WORM_HIGH', 'first_seen': '2017-11-13T19:49:24.459Z', 'last_updated': '2017-11-14T14:55:02.467Z', 'confidence': 'high', 'intention': 'malicious', 'category': 'worm', 'metadata': {'org': 'PE Tetyana Mysyk', 'rdns': '', 'rdns_parent': '', 'datacenter': 'ProHoster.info', 'asn': 'AS25092', 'os': '', 'link': '', 'tor': False}}]}
>>> print(test.json())
{'ip': '193.201.224.109', 'status': 'ok', 'returned_count': 2, 'records': [{'name': 'SSH_SCANNER_LOW', 'first_seen': '2017-11-13T20:02:11.444Z', 'last_updated': '2017-11-14T15:09:02.251Z', 'confidence': 'low', 'intention': '', 'category': 'activity', 'metadata': {'org': 'PE Tetyana Mysyk', 'rdns': '', 'rdns_parent': '', 'datacenter': 'ProHoster.info', 'asn': 'AS25092', 'os': '', 'link': '', 'tor': False}}, {'name': 'SSH_WORM_HIGH', 'first_seen': '2017-11-13T19:49:24.459Z', 'last_updated': '2017-11-14T14:55:02.467Z', 'confidence': 'high', 'intention': 'malicious', 'category': 'worm', 'metadata': {'org': 'PE Tetyana Mysyk', 'rdns': '', 'rdns_parent': '', 'datacenter': 'ProHoster.info', 'asn': 'AS25092', 'os': '', 'link': '', 'tor': False}}]}
>>> ip = '193.201.224.109'
>>> print(ip)
193.201.224.109
>>> test = requests.post('http://api.greynoise.io:8888/v1/query/ip', data={'ip': ip})
>>> print(ip)
193.201.224.109
>>> test.json()
{'ip': '193.201.224.109', 'status': 'ok', 'returned_count': 2, 'records': [{'name': 'SSH_SCANNER_LOW', 'first_seen': '2017-11-13T20:02:11.444Z', 'last_updated': '2017-11-14T15:09:02.251Z', 'confidence': 'low', 'intention': '', 'category': 'activity', 'metadata': {'org': 'PE Tetyana Mysyk', 'rdns': '', 'rdns_parent': '', 'datacenter': 'ProHoster.info', 'asn': 'AS25092', 'os': '', 'link': '', 'tor': False}}, {'name': 'SSH_WORM_HIGH', 'first_seen': '2017-11-13T19:49:24.459Z', 'last_updated': '2017-11-14T14:55:02.467Z', 'confidence': 'high', 'intention': 'malicious', 'category': 'worm', 'metadata': {'org': 'PE Tetyana Mysyk', 'rdns': '', 'rdns_parent': '', 'datacenter': 'ProHoster.info', 'asn': 'AS25092', 'os': '', 'link': '', 'tor': False}}]}
>>> test2 = requests.post('http://api.greynoise.io:8888/v1/query/ip', data={'ip': ip})
>>> test2.content
b'{"ip":"193.201.224.109","status":"ok","returned_count":2,"records":[{"name":"SSH_SCANNER_LOW","first_seen":"2017-11-13T20:02:11.444Z","last_updated":"2017-11-14T15:09:02.251Z","confidence":"low","intention":"","category":"activity","metadata":{"org":"PE Tetyana Mysyk","rdns":"","rdns_parent":"","datacenter":"ProHoster.info","asn":"AS25092","os":"","link":"","tor":false}},{"name":"SSH_WORM_HIGH","first_seen":"2017-11-13T19:49:24.459Z","last_updated":"2017-11-14T14:55:02.467Z","confidence":"high","intention":"malicious","category":"worm","metadata":{"org":"PE Tetyana Mysyk","rdns":"","rdns_parent":"","datacenter":"ProHoster.info","asn":"AS25092","os":"","link":"","tor":false}}]}'
>>> test2.text
'{"ip":"193.201.224.109","status":"ok","returned_count":2,"records":[{"name":"SSH_SCANNER_LOW","first_seen":"2017-11-13T20:02:11.444Z","last_updated":"2017-11-14T15:09:02.251Z","confidence":"low","intention":"","category":"activity","metadata":{"org":"PE Tetyana Mysyk","rdns":"","rdns_parent":"","datacenter":"ProHoster.info","asn":"AS25092","os":"","link":"","tor":false}},{"name":"SSH_WORM_HIGH","first_seen":"2017-11-13T19:49:24.459Z","last_updated":"2017-11-14T14:55:02.467Z","confidence":"high","intention":"malicious","category":"worm","metadata":{"org":"PE Tetyana Mysyk","rdns":"","rdns_parent":"","datacenter":"ProHoster.info","asn":"AS25092","os":"","link":"","tor":false}}]}'
>>> print(test2.json())

after importing pprint
>>> pprint(test2.json())
{'ip': '193.201.224.109',
 'records': [{'category': 'activity',
              'confidence': 'low',
              'first_seen': '2017-11-13T20:02:11.444Z',
              'intention': '',
              'last_updated': '2017-11-14T15:09:02.251Z',
              'metadata': {'asn': 'AS25092',
                           'datacenter': 'ProHoster.info',
                           'link': '',
                           'org': 'PE Tetyana Mysyk',
                           'os': '',
                           'rdns': '',
                           'rdns_parent': '',
                           'tor': False},
              'name': 'SSH_SCANNER_LOW'},
             {'category': 'worm',
              'confidence': 'high',
              'first_seen': '2017-11-13T19:49:24.459Z',
              'intention': 'malicious',
              'last_updated': '2017-11-14T14:55:02.467Z',
              'metadata': {'asn': 'AS25092',
                           'datacenter': 'ProHoster.info',
                           'link': '',
                           'org': 'PE Tetyana Mysyk',
                           'os': '',
                           'rdns': '',
                           'rdns_parent': '',
                           'tor': False},
              'name': 'SSH_WORM_HIGH'}],
 'returned_count': 2,
 'status': 'ok'}
>>> 

'''
