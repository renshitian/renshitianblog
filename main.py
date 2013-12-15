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

from datetime import *

def createKeyForBlog(blogName,user,date):
  return ndb.Key('Blog',blogName,user,date)




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


class ViewPost:
  blogName=''
  owner=''
  title=''
  content=''
  def __init__(self,blogName,owner,title,content,date):
    self.blogName = blogName
    self.date = date
    self.owner = owner
    self.title = title
    #set to 500 when finished
    self.content = content[:500]


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
            
        else:
            context['login_url'] = users.create_login_url(self.request.uri)
            context['login_text'] = "Log In"
        query = BlogEntry.query().order(-BlogEntry.date)
        context['blogs'] = query
        self.response.write(template.render(os.path.join(os.path.dirname(__file__),'index.html'),context))

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

        queryBlog = BlogEntry.query(BlogEntry.blogName==blog,BlogEntry.owner==str(users.get_current_user()))
        blogObject = queryBlog.get()
        parent_key = createKeyForBlog(blogObject.blogName,blogObject.owner,str(blogObject.date))
        title = cgi.escape(self.request.get('title'))
        content = cgi.escape(self.request.get('content'))
        owner = str(users.get_current_user())
        post = PostEntry(parent=parent_key)
        post.blogName = blog
        post.owner = owner
        post.title = title
        post.content = content
        post.put()
        
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
  maxP = 10
  context={
    'display_user_panel' : 'none',
    'display_nextpage' : 'none',
    'blogName' : '',
    'posts' : [],
    'owner' : ''
    }


  def createViewPosts(self,query):
    viewPosts=[]
    for post in query:
      tmp = ViewPost(post.blogName,post.owner,post.title,post.content,post.date)
      viewPosts.append(tmp)
    return viewPosts
  
  def get(self):
    if users.get_current_user():
      self.context['display_user_panel'] = 'inline'
    else:
      self.context['display_user_panel'] = 'none'
      
    blogName = self.request.get('blogName')
    owner = self.request.get('owner')
    pageNo = '1'
    self.context['page']=pageNo
    self.context['blogName'] = blogName
    self.context['owner'] = owner
    queryBlog = BlogEntry.query(BlogEntry.blogName==blogName,BlogEntry.owner==owner)
    blogObject = queryBlog.get()
    parent_key = createKeyForBlog(blogObject.blogName,blogObject.owner,str(blogObject.date))
    query = PostEntry.query(ancestor=parent_key).order(-PostEntry.date)
   
    postList=[]
    #used for ViewPost object for content of 500 chars

    
    if query.count() > self.maxP*int(pageNo):
      self.context['display_nextpage'] = 'inline'         
    else:
      self.context['display_nextpage'] = 'none'

    n=1
    iterator = query.iter()

    while iterator.has_next() and n<=self.maxP*int(pageNo):
      if n > self.maxP*(int(pageNo)-1):
        postList.append(iterator.next())
      else:
        iterator.next()
      n=n+1

    viewPosts= self.createViewPosts(query)
    #gen ju page no lai pan duan dang qian ye mian xu yao xian shi na xie tiao posts, ran hou pan duan shi fou hai you sheng xia de post ru you display next page link
    #mei you le ze display:none next page link
    self.context['posts'] = viewPosts
    
    self.response.write('page no is 1</br>'+'query count = '+str(query.count())+'</br>')
    self.response.write(template.render(os.path.join(os.path.dirname(__file__),'viewBlog.html'),self.context))



  def post(self):
    if users.get_current_user():
      self.context['display_user_panel'] = 'inline'
    else:
      self.context['display_user_panel'] = 'none'

    blogName = self.request.get('blogName')
    owner = self.request.get('owner')
    pageNo = cgi.escape(self.request.get('pageno'))

    self.context['blogName'] = blogName
    self.context['owner'] = owner
    queryBlog = BlogEntry.query(BlogEntry.blogName==blogName,BlogEntry.owner==owner)
    blogObject = queryBlog.get()
    parent_key = createKeyForBlog(blogObject.blogName,blogObject.owner,str(blogObject.date))
    query = PostEntry.query(ancestor=parent_key).order(-PostEntry.date)
    postList = []
    p = int(pageNo)
    p=p+1
    pageNo = str(p)
    if query.count() > self.maxP*int(pageNo):
      self.context['display_nextpage'] = 'inline'      
    else:
      self.context['display_nextpage'] = 'none'
    
    self.response.write('page no is '+str(p)+'</br>'+'query count = '+str(query.count())+'</br>')

    n=1
    iterator = query.iter()
    
    while iterator.has_next() and n<=self.maxP*int(pageNo):

      if n > self.maxP*(int(pageNo)-1):
        postList.append(iterator.next())
      else:
        iterator.next()
      n=n+1
      
    viewPosts=self.createViewPosts(query)
    self.context['posts'] = viewPosts
    self.context['page'] = str(p)
    #self.context['posts'] = postList
    self.response.write(template.render(os.path.join(os.path.dirname(__file__),'viewBlog.html'),self.context))


#todo ::::::: print all the blogs and set a href for each blog with http-get parameters of blogName and then href to /viewPost


#todo::: after doing the viewBlogHandler, do the feature 4 here            
class viewPostHandler(webapp2.RequestHandler):
    def get(self):
            blogName = self.request.get('blogName')
            postTitle = self.request.get('title')
            owner = self.request.get('owner')
            queryBlog = BlogEntry.query(BlogEntry.blogName==blogName,BlogEntry.owner==owner)
            blogObject = queryBlog.get()
            parent_key = createKeyForBlog(blogObject.blogName,blogObject.owner,str(blogObject.date))
            query = PostEntry.query(PostEntry.title==postTitle,ancestor=parent_key)
            post = query.get()
            context={}
            context['post'] = post
            self.response.write(template.render(os.path.join(os.path.dirname(__file__),'viewPost.html'),context))     






app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/createBlog', createBlogHandler),
    ('/writePost',writePostHandler),
    ('/manageBlog',manageBlogHandler),
    ('/viewPost',viewPostHandler),
    ('/viewBlog',viewBlogHandler),
], debug=True)
