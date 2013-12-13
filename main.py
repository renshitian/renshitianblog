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

import os
import webapp2
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

class MainHandler(webapp2.RequestHandler):

    def get(self):
        context = {
            'welcome': 'Welcome to Blog',
            'post': []
        }
        if users.get_current_user():
            context['login_url'] = users.create_logout_url(self.request.uri)
            context['login_text'] = "Log Out"
            context['welcome'] = 'Hello  '+str(users.get_current_user())

            
        else:
            context['login_url'] = users.create_login_url(self.request.uri)
            context['login_text'] = "Log In"

        context['post'].append('post111')
        context['post'].append('post222')
        self.response.write(template.render(os.path.join(os.path.dirname(__file__),'index.html'),context))

class writeHandler(webapp2.RequestHandler):
    def get(self):
        context = {}
        context['welcome'] = str(users.get_current_user())
        self.response.write(template.render(os.path.join(os.path.dirname(__file__),'writeBlog.html'),context))



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/writeBlog',writeHandler)
], debug=True)
