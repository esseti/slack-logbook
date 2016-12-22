#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# author: stefano tranquillini
import json

from datetime import datetime, timedelta
import webapp2

from google.appengine.api import urlfetch
import urllib
from apiclient import discovery
from google.appengine.ext import deferred

from oauth2client.contrib.appengine import AppAssertionCredentials

from cfg import *


def post_log(message, vote, user_name, url):
    '''
    Deffred task to post data on spreadsheet and notify via slack.
    This to avoid the 3000ms delay

    Args:
        message:
        vote:
        user_name:
        url:

    Returns:

    '''
    day = datetime.now().date()
    day -= timedelta(days=1)
    credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/spreadsheets')
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', credentials=credentials,
                              discoveryServiceUrl=discoveryUrl)

    body = {'values': [[day.strftime('%Y-%m-%d'), message, vote]]}
    service.spreadsheets().values().append(spreadsheetId=SHEET_ID,
                                           range='%s!A1' % user_name, body=body,
                                           valueInputOption='USER_ENTERED').execute()

    response_message = {
        "response_type": "ephimeral",
        "text": "Added"
    }
    urlfetch.fetch(url=url,
                   payload=json.dumps(response_message),
                   method=urlfetch.POST, headers={"Content-Type": 'application/json'})

class LogBookHandler(webapp2.RequestHandler):
    @staticmethod
    def make_dict(body):
        '''
        Creates the dictonary from url params
        Args:
            body:

        Returns:

        '''
        data = dict()
        all_data = urllib.unquote_plus(body).split("&")
        for d in all_data:
            ds = d.split("=")
            if ds[0]:
                data[ds[0]] = ds[1]
        return data



    def logbook(self, data):
        '''
        It sends  the data to be processed and return a message to slack.
        We give back resutl in less than 3000ms and can then process the data.
        Args:
            data:

        Returns:

        '''
        message, vote = data['text'].strip().split('|')
        response_message = {
            "response_type": "ephemeral",
            "text": "Posting data .. please wait "
        }
        self.response.write(json.dumps(response_message))
        deferred.defer(post_log, str(message), int(vote), str(data['user_name']), str(data['response_url']))

        return

    def post(self):
        '''
        Handler of the post data
        checks the token and then calls the log funcion.
        Returns:

        '''
        data = self.make_dict(self.request.body)

        if data['token'] != TOKEN:
            self.response.write("Not allowed")
            return
        self.response.headers.add_header('Content-Type', 'application/json')

        if data['text'].startswith("info"):
            response_message = {
                "response_type": "in_channel",
                "text": "The file is located here <https://docs.google.com/spreadsheets/d/%s/edit>" % SHEET_ID
            }
            self.response.write(json.dumps(response_message))
        else:

            self.logbook(data)
        return


app = webapp2.WSGIApplication([
    ('/', LogBookHandler)
], debug=True)
