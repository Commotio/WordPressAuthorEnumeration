#!/usr/bin/env python3

import requests
import sys
import datetime
from glom import glom
import json
from bs4 import BeautifulSoup
import urllib3
from lxml.html import fromstring
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

black = lambda text: '\033[0;30m' + text + '\033[0m'                                                                                                                                                                                                                                                                       
red = lambda text: '\033[1;31m' + text + '\033[0m'                                                                                                                                                                                                                                                                         
green = lambda text: '\033[1;32m' + text + '\033[0m'                                                                                                                                                                                                                                                                       
yellow = lambda text: '\033[1;33m' + text + '\033[0m'                                                                                                                                                                                                                                                                      
blue = lambda text: '\033[0;34m' + text + '\033[0m'                                                                                                                                                                                                                                                                        
magenta = lambda text: '\033[0;35m' + text + '\033[0m'                                                                                                                                                                                                                                                                     
cyan = lambda text: '\033[0;36m' + text + '\033[0m'                                                                                                                                                                                                                                                                        
white = lambda text: '\033[0;37m' + text + '\033[0m'

def help_menu():
		print("----------------------------------------------------------------------------------------------------------------------")                   
		print("Usage:\n")                                                                                                                                 
		print("Enumerate the authors of a wordpress implementation:")
		print(yellow("  python3 wordpressAuthSlammer.py https://target.com\n"))
		print("----------------------------------------------------------------------------------------------------------------------") 

def ascii_art():
	print(" __       __                            __  _______                                                  ______               __      __  ")     
	print("|  \  _  |  \                          |  \|       \                                                /      \             |  \    |  \      ")
	print("| $$ / \ | $$  ______    ______    ____| $$| $$$$$$$\  ______    ______    _______   _______       |  $$$$$$\ __    __  _| $$_   | $$____  ")
	print("| $$/  $\| $$ /      \  /      \  /      $$| $$__/ $$ /      \  /      \  /       \ /       \      | $$__| $$|  \  |  \|   $$ \  | $$    \ ")
	print("| $$  $$$\ $$|  $$$$$$\|  $$$$$$\|  $$$$$$$| $$    $$|  $$$$$$\|  $$$$$$\|  $$$$$$$|  $$$$$$$      | $$    $$| $$  | $$ \$$$$$$  | $$$$$$$\ ")
	print("| $$ $$\$$\$$| $$  | $$| $$   \$$| $$  | $$| $$$$$$$ | $$   \$$| $$    $$ \$$    \  \$$    \       | $$$$$$$$| $$  | $$  | $$ __ | $$  | $$ ")
	print("| $$$$  \$$$$| $$__/ $$| $$      | $$__| $$| $$      | $$      | $$$$$$$$ _\$$$$$$\ _\$$$$$$\      | $$  | $$| $$__/ $$  | $$|  \| $$  | $$ ")
	print("| $$$    \$$$ \$$    $$| $$       \$$    $$| $$      | $$       \$$     \|       $$|       $$      | $$  | $$ \$$    $$   \$$  $$| $$  | $$ ")
	print(" \$$      \$$  \$$$$$$  \$$        \$$$$$$$ \$$       \$$        \$$$$$$$ \$$$$$$$  \$$$$$$$        \$$   \$$  \$$$$$$     \$$$$  \$$   \$$ ")                                                                                                                                     
	print()
	print(green(" Tool Description         :: Wordpess Author Enumeration"))
	print(green(" Author                   :: Milashner"))
	print()
	print("----------------------------------------------------------------------------------------------------------------------") 
	print()

def getMainTitle(base_url):
	response = requests.get(base_url)
	tree = fromstring(response.content)
	mainTitle = tree.findtext('.//title')
	mainTitle = mainTitle.strip()
	mainTitle = mainTitle.replace("\r", "")
	mainTitle = mainTitle.replace("\t", "")
	return mainTitle

def checkUserListing(base_url,headers):
	try:
		url = base_url + "wp-json/wp/v2/users/?per_page=100&page=1"
		response = requests.get(url, headers=headers, verify=False, allow_redirects=False)
		res = json.loads(response.text)
		specs = {"id":['id'],"name":['name']}
		output = glom(res,specs)
		names = []
		new_pair = []

		counter = 0
		for id in output["id"]:
			new_pair = [str(id), output["name"][counter]]
			names.append(new_pair)
			counter +=1
	
		print("User Listing Page Available - Pulling Authors")
		return getResults(names)

	except:
		return False

def main():
	headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
	if len(sys.argv) != 2:
		help_menu()
		exit()
	base_url = sys.argv[1]

	if base_url[-1] != '/':
		base_url = base_url + '/'

	ascii_art()

	userListing = checkUserListing(base_url,headers)
	if not userListing:
		print()
		print('No user listing found. Attempting enumeration via "author" param')
		names = []
		not_found_count = 0
		authorId = 0

		print("{:<12} | {:<12} | {:<6}".format('STATUS CODE', 'AUTHOR ID', 'AUTHOR'))
		print("--------------------------------------------------") 
		mainTitle = getMainTitle(base_url)
		response = None
		while not_found_count < 10:
			try:
				url = base_url + '?author=' + str(authorId)
				response = requests.get(url, headers=headers, verify=False, allow_redirects=False)
			except (KeyboardInterrupt, SystemExit):
				break
			except:
				print("error - no response")
				not_found_count += 1

			if response is not None:
				try:
					tree = fromstring(response.content)
					name = tree.findtext('.//title')
					name = name.strip()
					name = name.replace("\r", "")
					name = name.replace("\t", "")
					if name == mainTitle:
						name = "Not Found"
					else:
						print("{:12} | {:12} | Not Found".format(str(response.status_code), str(authorId)))
						name = "Not Found"
				except:
					if response.status_code == 301:
						if response.headers['Location'][-1] != '/':
							name = response.headers['Location'].split('/')[-1]
						else:	
							name = response.headers['Location'].split('/')[-2]
						print("{:12} | {:12} | {:<50}".format(str(response.status_code), str(authorId), name))
					else:	
						print("{:12} | {:12} | Not Found".format(str(response.status_code), str(authorId)))
						name = "Not Found"

				if response.status_code == 404 or name == "Not Found":
					not_found_count += 1
				else:
					not_found_count = 0
					new_pair = [authorId, name]
					names.append(new_pair)

			authorId += 1
			response = None

		getResults(names)

def getResults(names):
	print()
	print("{:<12} | {:<50}".format('AUTHOR ID', 'AUTHOR'))
	print("--------------------------------------------------")
	for pair in names:
		print("{:<12} | {:<50}".format(yellow(str(pair[0])), yellow(pair[1])))
	print("--------------------------------------------------\n")
	
	date_time = datetime.datetime.now()
	file_name = date_time.strftime("wordpress_author_enum" + "%m-%d-%y-%X.txt")
	file_name = file_name.replace(":", "-")

	outfile = open(file_name, "w+")
	outfile.write("Author ID;Name;\n")
	for pair in names:
		t = 'ID = ' + str(pair[0])
		outfile.write(t + ";" + pair[1] + ";\n")
	print(yellow("Results written in CSV format to: " + file_name))
	print()
	outfile.close()

	return True

main()
