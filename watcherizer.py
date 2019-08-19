from urllib.parse import urljoin
from bs4 import BeautifulSoup
from random import randint
from colorama import Fore,init
from flask import request
from flask import Flask
from time import sleep
from glob import glob
import threading
import datetime
import platform
import requests
import difflib
import hashlib
import ntpath
import slack
import json
import sys
import re
import os


slack_channel = ""
slack_token   = ""

sleep_time    = 60 * randint(30, 60)
report_fmt    = """
 {target} :: {changes}
"""

app = Flask(__name__)

if os.path.isfile('watch.db'):
	watch_list = set([l.strip() for l in open('watch.db','r').readlines()])
else:
	watch_list = set()


def write(f,c): open(f,'w').write(c)
def read(f):    return open(f,'r').read()
def get(url):
	try:
		return requests.get(url).text
	except Exception as e:
		return ''

def diff(old,new):
	diff = difflib.unified_diff(old.split('\n'),new.split('\n'), lineterm='',fromfile='stored version',tofile='live version')
	return '\n'.join(diff)

def slackmsg(msg):
	sc = slack.WebClient(token=slack_token)
	sc.chat_postMessage(channel=slack_channel,text=msg)

def slackdiff(comment,content):
	sc = slack.WebClient(token=slack_token)
	sc.files_upload(channels=slack_channel,filetype="diff",content=content,initial_comment=comment)

def slugify(value):
    value = value.replace("://", "_")
    value = value.replace("/", "_")
    value = value.replace(":", "_")
    value = value.replace("\\", "_")
    value = value.replace(".", "_")
    return value.strip()

def tokenize(content):
	rules = [rule.strip() for rule in open("ignore.rules","r").readlines()]
	for rule in rules: content = re.sub(rule, '', content)
	return hashlib.md5(content.encode('utf-8')).hexdigest()

def extract_sources(url,content):
	soup    = BeautifulSoup(content,features="lxml")
	sources = soup.findAll('script',{"src":True})
	src2dict = {}
	for source in sources:
		abspath = urljoin(url + "/",source['src'])
		if abspath == None: continue
		source_content = get(abspath).encode('utf-8').decode('utf-8')
		md5hash = tokenize(source_content)
		src2dict.update({abspath:{'md5hash': md5hash,'content': source_content}})
	return src2dict

def scrape(url):
	try:
		content = get(url)
		soup    = BeautifulSoup(content,features="lxml")
		return { 'url': url, 'sources': extract_sources(url, content),
					'md5hash': tokenize(content),'content': soup.prettify()}
	except Exception as e:
		return None


def compare(stored,current):
	results = {'msg':[]}
		
	new_sources     = [x for x in set(current['sources'].keys()) if x not in set(stored['sources'].keys())]
	removed_sources = [x for x in set(stored['sources'].keys()) if x not in set(current['sources'].keys())]

	for source in stored['sources'].keys():
		if not source in current['sources'].keys(): continue

		if current['sources'][source]['md5hash'] != stored['sources'][source]['md5hash']:
			results['msg'].append("edited: %s" % source)
	
	[results['msg'].append("added: %s" % new) for new in new_sources]
	[results['msg'].append("removed: %s" % rm) for rm in removed_sources]

	if stored['md5hash'] == current['md5hash']:
		if results['msg'] == []: return 0
		results['msg'].append("html: same")
	else:
		results['msg'].append("html: edited")
		results.update({'body_diff': diff(stored['content'],current['content'])})

	return results
	
def scan_changes(target):

	timestamp = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
	slugified = slugify(target)
	path      = 'storage/%s_%s' % (timestamp,slugified)
	scraped   = scrape(target)

	if scraped == None: return None

	if glob("storage/*_%s" % slugified):
		stored_path = ntpath.basename(max(glob("storage/*_%s" % slugified), key=os.path.getctime))
	else:
		stored_path = None

	if stored_path:
		stored           = json.loads( read('storage/%s' % stored_path) )
		compare_result   =  compare(stored, scraped)
		if compare_result == 0: return

		if compare_result:
			write(path, json.dumps(scraped))
			return compare_result
	else:
		write(path, json.dumps(scraped))
	
	return None

def scanner():
	slackmsg("Watcherizer is up! :tada:")
	while 1:
		for target in watch_list:
			changes    =  scan_changes(target)
			if not changes: continue

			report_msg = report_fmt.format(target=target,changes='\n - '.join(changes['msg'][::-1]))
			if not 'body_diff' in changes:
				slackmsg(report_msg)
			else:
				slackdiff(report_msg,changes['body_diff'])

		open('watch.db','w').write('\n'.join(watch_list))
		sleep(sleep_time)



@app.route("/monitor",methods=['POST'])
def monitor():
	target = request.form.get('text')
	if get(target):
			watch_list.add(target)
			return "Added %s to watch list" % (target)
	else:
		return "Invalid target: %s" % target

@app.route("/list",methods=['POST'])
def wlist():
	if len(watch_list) == 0:
		return 'Watch list is empty'
	return 'Watch list target(s):\n- ' + '\n- '.join(watch_list)

@app.route("/watchtime",methods=['POST'])
def watchtime():
	global sleep_time
	slack_msg = request.form.get('text').strip()
	if slack_msg:
		sleep_time = int(slack_msg)
		return 'Watching frequency updated to %i second(s)' % sleep_time
	return 'Current watching frequency is: %i second(s)' % sleep_time

@app.route("/remove",methods=['POST'])
def wremove():
	target = request.form.get('text').strip()
	if target in watch_list:
		watch_list.remove(target)
		return '%s removed from the watching list' % (target)
	else:
		return '%s is not on the watching list' % (target)


init(autoreset=1)
print("""{R}  __    __      _       _               _              
 / / /\ \ \__ _| |_ ___| |__   ___ _ __(_)_______ _ __ 
 \ \/  \/ / _` | __/ __| '_ \ / _ \ '__| |_  / _ \ '__|
  \  /\  / (_| | || (__| | | |  __/ |  | |/ /  __/ |   
   \/  \/ \__,_|\__\___|_| |_|\___|_|  |_/___\___|_|

 {W}[{R}GITHUB{W}]: {B}https://github.com/BitTheByte/watcherizer
 {W}[{R}VERSION{W}]: 1.0
 {W}[{R}ENV{W}]:
 {W} |> PYTHON: {ENV_PYTHON}
 {W} |> PLATFORM: {ENV_PLATFORM} {ENV_RELEASE}
""".format(
 	ENV_PLATFORM=platform.system(),
 	ENV_RELEASE=platform.release(),
 	ENV_PYTHON=platform.python_version(),
	G=Fore.LIGHTGREEN_EX,
	LB=Fore.LIGHTBLACK_EX,
	B=Fore.CYAN,
	R=Fore.RED,
	W=Fore.WHITE,
	Y=Fore.YELLOW
))
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

if not slack_channel or not slack_token:
	print(" Please edit [slack_channel] and [slack_token] before running this bot")
else:
	threading.Thread(target=scanner).start()
	app.run(host='0.0.0.0',port=1337)