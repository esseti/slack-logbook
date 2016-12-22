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
from apiclient import discovery
from google.appengine.api import urlfetch
from oauth2client.contrib.appengine import AppAssertionCredentials

from cfg import *

class ReminderHandler(webapp2.RequestHandler):


    def slack(self,  channel):
        '''
        send notification via slack webhook
        Args:
            channel:

        Returns:

        '''
        payload = json.dumps({
            "channel": '@'+channel,
            "username": USERNAME,
            "icon_emoji": ICON,
            "color": "good",
            "title": "Hi %s its time to log your work" % channel,
        })

        r = urlfetch.fetch(url=INCOMING_WH,
                           payload=payload,
                           method=urlfetch.POST,headers={"Content-Type": 'application/json'})
        return True

    def get(self):
        '''
        Send a message to all the users to log their data.
        It's a cron task

        Returns:

        '''
        #iterate over users
        for user in USERS:
            self.slack(user)

class NextDayHandler(webapp2.RequestHandler):

    def get(self):
        '''
        Adds the empty log when the ady before was not logged.
        It's a cron task

        :return:
        '''

        for username in USERS:
            credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/spreadsheets')
            discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
            service = discovery.build('sheets', 'v4', credentials=credentials,
                                      discoveryServiceUrl=discoveryUrl)
            #able to handle 1000 entrys, ~3 years. should be enough
            res = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range='%s!A1:A1000'%username).execute()
            #day of the last entry
            ld = res['values'][-1][0]
            fd = datetime.strptime(ld,'%Y-%m-%d').date()
            #check the expected day of the last log (today -2 days since this is run at 4AM)
            pd = datetime.now().date()
            pd -= timedelta(days=2)
            if fd != pd:
                # if there was no log
                if pd.weekday()>=5:
                    # if was weekend then this
                    body = {'values': [[pd.strftime('%Y-%m-%d'), "weekend"]]}
                else:
                    #else this
                    body = {'values': [[pd.strftime('%Y-%m-%d'), "NO LOG"]]}
                service.spreadsheets().values().append(spreadsheetId=SHEET_ID,
                                                       range='%s!A1' % username, body=body,
                                                       valueInputOption='USER_ENTERED').execute()
            print "done"


app = webapp2.WSGIApplication([
    ('/dr', ReminderHandler),
    ('/nd', NextDayHandler)
], debug=False)
