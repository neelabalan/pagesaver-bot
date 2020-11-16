import json
import signal
import os
from datetime import datetime
from collections import namedtuple
import requests

# from stackoverflow
# https://stackoverflow.com/a/44859638/4873716
class dictpath(dict):
    def get(self, path, default=None):
        keys = path.split(".")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)
            if not val:
                break
        return val

class TelegramBot:
    def __init__(self, token):
        self.method        = ''
        self.baseUrl       = 'https://api.telegram.org/bot{}'.format(token)
        self.lastUpdated   = None
        self.lastMessageId = None
        self.chatId        = None
        self.pollflag      = True

    def getMethodUrl(self, method):
        ''' get url with method '''
        return self.baseUrl + '/' + method

    def _getUpdate(self):
        ''' get the latest update '''
        updates = requests.get( self.getMethodUrl('getUpdates') ).json()
        return updates.get('result')[-1] 

    def _getLatestMessageIdTime(self, update):
        ''' returns the latest message.id and time '''
        latestMessageId = dictpath(update).get('message.message_id')
        latestTime = dictpath(update).get('message.date')
        return latestMessageId, latestTime

    def poll(self, onReceive, forceUpdate=False):
        ''' start polling for message  on receive invoke callback ''' 
        while self.pollflag:
            update = self._getUpdate()
            latestMessageId, latestTime = self._getLatestMessageIdTime(update) 
            self.chatId = dictpath(update).get('message.chat.id') 
            self.lastUpdated = latestTime if forceUpdate else self.lastUpdated
            if self.lastUpdated != latestTime:
                print(dictpath(update).get('message.text'))
                try:
                    self.lastMessageId = latestMessageId if not self.lastMessageId == latestMessageId else self.lastMessageId
                    self.lastUpdated = latestTime if not self.lastUpdated or self.lastUpdated < latestTime else self.lastUpdated 
                    onReceive(dictpath(update).get('message.text'))
                except:
                    self.postMessage('Error extracting the url')
            forceUpdate = False

    def getReply(self):
        ''' handles the reply to a question posted '''
        self.pollflag = False # need to stop the polling  

        latestMessageId = self.lastMessageId
        ## wait for reply
        while latestMessageId == self.lastMessageId:
            update = self._getUpdate()
            latestMessageId, _ = self._getLatestMessageIdTime(update)
        ## loop ends when there is new update
        self.pollflag = True
        return dictpath(update).get('message.text')


    def postMessage(self, text):
        ''' posts a message to the bot '''
        # creating the request
        requests.post(
            url = self.baseUrl + '/' + 'sendMessage',
            data = dict(
                chat_id     = self.chatId, 
                text        = text,
                parse_mode  = 'MarkdownV2'
            )
        )

    def postFile(self, file):
        ''' posts a file to the bot '''
        requests.post(
            url   = self.baseUrl + '/' + 'sendDocument',
            data  = dict(
                chat_id     = self.chatId, 
                document    = 'attach://file'
            ),
            files = dict(
                file = open(file, 'rb')
            )
        )

class CommandHandler:
	def __init__(self, TelegramBot):
		''' get the TelegramBot object as input '''
		pass


