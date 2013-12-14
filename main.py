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
import cgi
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb




class BlogEntry(ndb.Model):
  blogName = ndb.StringProperty()
  date = ndb.DateTimeProperty(auto_now=True)
  owner = ndb.StringProperty()


class MainHandler(webapp2.RequestHandler):

    def get(self):
        context = {
            'display1' : 'display:none',
            'welcome': 'Welcome to Blog',
            'blogs' : []
        }
        if users.get_current_user():
            context['login_url'] = users.create_logout_url(self.request.uri)
            context['login_text'] = "Log Out"
            context['display1'] = 'display:inline'
            context['welcome'] = 'Hello  '+str(users.get_current_user())
            
            #for result in query:
            #    blog = { 'blogName' : str(result.blogName),
            #             'owner': str(result.owner)
            #             }
            #    context['blogs'].append([blog])
            
        else:
            context['login_url'] = users.create_login_url(self.request.uri)
            context['login_text'] = "Log In"
        query = BlogEntry.query().order(-BlogEntry.date)
        context['blogs'] = query
        self.response.write(template.render(os.path.join(os.path.dirname(__file__),'index.html'),context))

#step 2: write post to blog, provide a dropdown list to choose which blog to write post for
class writePostHandler(webapp2.RequestHandler):
    context={
        'display1' : '',
        'display2' : '',
        'welcome' : ''
        }
    def get(self):
        if users.get_current_user():
            
            self.context['welcome']='Hello '+str(users.get_current_user())
            self.context['display1'] = 'display:inline'
            self.context['display2'] = 'display:none'
            self.response.write(template.render(os.path.join(os.path.dirname(__file__),'writePost.html'),self.context))           
            #self.response.write(self.request.get('blogName')) used for get http-get method var, if can get, hide the dropdown list, it not show dropdown list to choose
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        self.context['display1'] = 'display:none'
        self.context['display2'] = 'display:inline'
        self.context['welcome']='Hello '+str(users.get_current_user())
        self.response.write(template.render(os.path.join(os.path.dirname(__file__),'writePost.html'),self.context))


class createBlogHandler(webapp2.RequestHandler):
    context={
        'display1' : '',
        'display2' : '',
        'welcome' : ''
        }
    def get(self):
        if users.get_current_user():
            self.context['welcome']='Hello '+str(users.get_current_user())
            self.context['display1'] = 'display:inline'
            self.context['display2'] = 'display:none'
            self.response.write(template.render(os.path.join(os.path.dirname(__file__),'createBlog.html'),self.context))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        self.context['display1'] = 'display:none'
        self.context['display2'] = 'display:inline'
        blogName = cgi.escape(self.request.get('name'))
        self.context['name'] = blogName
        self.context['welcome']='Hello '+str(users.get_current_user())
        b = BlogEntry()
        b.owner = str(users.get_current_user())
        b.blogName = blogName
        b.put()
        self.response.write(template.render(os.path.join(os.path.dirname(__file__),'createBlog.html'),self.context))


# step 1 : manage user's own blog, list all the blogs and add a href to write post change to template
class manageBlogHandler(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            query = BlogEntry.query(BlogEntry.owner==str(users.get_current_user()))
            self.response.write('manage blog</br>')
            for blog in query:
                self.response.write('<a href = "/viewPost?blogName='+blog.blogName+'">'+blog.blogName+'</a></br>')#here writePost should be replaced by viewPost
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
#step 3: select posts from one blog provided from http-get method, show it
class viewPostHandler(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            blogName = self.request.get('blogName')
            self.response.write('View Post from blog: '+blogName)
            
        else:
            self.redirect(users.create_login_url(self.request.uri))
        



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/createBlog', createBlogHandler),
    ('/writePost',writePostHandler),
    ('/manageBlog',manageBlogHandler),
    ('/viewPost',viewPostHandler)
], debug=True)
