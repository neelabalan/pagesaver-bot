import os
import re
import logging
import subprocess
from telegram import TelegramBot
from urllib.parse import urlparse

API_TOKEN = ''
bot = TelegramBot(API_TOKEN)

def validUrl(url):
    ''' checks for a valid url '''
    tokens = urlparse(url)
    return True if tokens.scheme in ("https", "http") and tokens.netloc else False

def extractUrl(text):
    ''' extract the url from the text (got this from stackoverflow) '''
    return re.search("(?P<url>https?://[^\s]+)", text).group("url")

def getHTMLDocument(url, filename):
	''' get the html document from monolith '''
	try:
		htmlFile = filename + '.hmtl'
		subprocess.run(['monolith', url, '-o', htmlFile], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL )
		return True
	except:
		return False

def meetsFileSizeLimit(file):
	byte = os.path.getsize(file)
	return True if byte/1000000 < 50 else False

def main(message):
	''' starts here '''
	url = extractUrl(message)
	if(validUrl(url)):
		bot.postMessage('send file name')
		reply = bot.getReply()
		filename = reply + '.html'
		bot.postMessage('you will be sent `{}` file in few minutes'.format(filename))
		subprocess.run(['./monolith', url, '-o', filename]) 
		if meetsFileSizeLimit(filename):
			bot.postFile(filename)
		else:
			bot.postMessage('download size is more than 50 MB')

		# restart poll after stop and force update to avoid message conflict
		bot.poll(onReceive=main, forceUpdate=True)
	else:
		bot.postMeesage('Not a valid URL')

# force update initially
bot.poll(onReceive=main, forceUpdate=True)
