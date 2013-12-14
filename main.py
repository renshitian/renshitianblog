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


class PostEntry(ndb.Model):
  blogName = ndb.StringProperty()
  date = ndb.DateTimeProperty(auto_now=True)
  owner = ndb.StringProperty()
  title = ndb.StringProperty()
  content = ndb.TextProperty()


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
        'display_form' : '',
        'display_write_success' : '',
        'welcome' : '',
        'blogs' : []
        }
    
    blogName = ''
    def get(self):
        if users.get_current_user():
            self.blogName = self.request.get('blogName')
            self.context['welcome']=('Author: '+str(users.get_current_user()))
            query = BlogEntry.query(BlogEntry.owner==str(users.get_current_user()))

            if self.blogName:
              self.context['blogName'] = self.blogName
              self.context['display_selection'] = 'display:none'
              self.context['display_form'] = 'display:inline'
              self.context['fromWhere'] = 'definedBlog'
              

            else:
              if query.count()>0:
                self.context['blogName'] = 'Choose Blog to Write Post: '
                self.context['display_selection'] = 'display:inline'
                self.context['display_form'] = 'display:inline'
                self.context['blogs'] = query
                self.context['fromWhere'] = 'selection'
              else:
                self.context['blogName'] = 'To Write Post, Create Blog First!!'
                self.context['display_form'] = 'display:none'
                
            self.context['display_write_success'] = 'display:none'
            self.response.write(template.render(os.path.join(os.path.dirname(__file__),'writePost.html'),self.context))           
            #self.response.write(self.request.get('blogName')) used for get http-get method var, if can get, hide the dropdown list, it not show dropdown list to choose
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        self.context['display_form'] = 'display:none'
        self.context['display_write_success'] = 'display:inline'
        self.context['welcome']='Hello '+str(users.get_current_user())
        fromWhere = cgi.escape(self.request.get('chooseFromWhere'))
        blog=''
        if fromWhere=='selection':
          blog=cgi.escape(self.request.get('choosenBlog'))
        else:
          blog=cgi.escape(self.request.get('definedBlog'))

        title = cgi.escape(self.request.get('title'))
        content = cgi.escape(self.request.get('content'))
        owner = str(users.get_current_user())
        post = PostEntry()
        post.blogName = blog
        post.owner = owner
        post.title = title
        post.content = content
        post.put()
        
        #self.response.write('blog: '+blog+'</br>')
        #self.response.write('owner'+str(users.get_current_user())+'</br>')
        #self.response.write('title: '+title+'</br>')
        #self.response.write('content: '+content+'</br>')
        

        
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


# step 1 : manage user's own blog, list all the blogs and add a href to  post change to template
class manageBlogHandler(webapp2.RequestHandler):
  context = {
    'welcome': 'Welcome to Blog',
    'blogs' : []
    }
  def get(self):
        if users.get_current_user():
          self.context['welcome'] = str(users.get_current_user())
          query = BlogEntry.query(BlogEntry.owner==str(users.get_current_user()))
          self.context['blogs'] = query
          self.response.write(template.render(os.path.join(os.path.dirname(__file__),'manageBlog.html'),self.context))
          if query.count()==0:
            self.response.write('No blogs, Create One!!')
        else:
          self.redirect(users.create_login_url(self.request.uri))

class viewBlogHandler(webapp2.RequestHandler):
  def get(self):
    blogName = self.request.get('blogName')
    self.response.write('view blog of '+blogName+'</br>')
    self.response.write('<a href = "/writePost?blogName='+blogName+'">Write Post</a></br>')
    query = PostEntry().query(PostEntry.blogName==blogName)
    for p in query:
      self.response.write('Post'+' title '+p.title+' content:'+ p.content+''+'</br>')



            
#step 3: select posts from one blog provided from http-get method, show it
class viewPostHandler(webapp2.RequestHandler):
    def get(self):
            blogName = self.request.get('blogName')
            self.response.write('View Post from blog: '+blogName)
            query = PostEntry().query(PostEntry.blogName==blogName)
            for p in query:
              self.response.write('Post: '+p.title)
            
        






app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/createBlog', createBlogHandler),
    ('/writePost',writePostHandler),
    ('/manageBlog',manageBlogHandler),
    ('/viewPost',viewPostHandler),
    ('/viewBlog',viewBlogHandler)
], debug=True)
