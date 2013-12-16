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
import re
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from google.appengine.api import images
from datetime import *

def createKeyForBlog(blogName,user,date):
  return ndb.Key('Blog',blogName,user,date)






class BlogEntry(ndb.Model):
  blogName = ndb.StringProperty()
  date = ndb.DateTimeProperty(auto_now=True)
  owner = ndb.StringProperty()


class PostEntry(ndb.Model):
  blogName = ndb.StringProperty()
  modifydate = ndb.DateTimeProperty(auto_now=True)
  owner = ndb.StringProperty()
  title = ndb.StringProperty()
  content = ndb.TextProperty()
  date = ndb.DateTimeProperty()
  tags = ndb.StringProperty(repeated=True)

class ImageEntry(ndb.Model):
  permaLink = ndb.StringProperty()
  image = ndb.BlobProperty()


class ViewPost:
  blogName=''
  owner=''
  title=''
  content=''
  tags=[]
  
  def __init__(self,blogName,owner,title,content,date,modifydate,tags):
    self.blogName = blogName
    self.date = date
    self.owner = owner
    self.title = title
    #set to 500 when finished
    self.content = content[:500]
    self.modifydate = modifydate
    self.tags = tags

class MainHandler(webapp2.RequestHandler):


  def collectTags(self):
    tags = set()
    query = PostEntry.query()
    for post in query:
        for tag in post.tags:
          tags.add(tag)
    return tags

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
      context['welcome'] = 'Hello '+str(users.get_current_user())
    else:
      context['login_url'] = users.create_login_url(self.request.uri)
      context['login_text'] = "Log In"
    query = BlogEntry.query()
    context['blogs'] = query
    context['tags'] = self.collectTags()
    self.response.write(template.render(os.path.join(os.path.dirname(__file__),'index.html'),context))
    #self.response.write('tags are '+str(self.collectTags()))

class writePostHandler(webapp2.RequestHandler):
    context={
        'display_form' : '',
        'display_write_success' : '',
        'welcome' : '',
        'title' : 'defalut title',
        'content' : 'defalut content',
        'blogs' : [],
        'update' : ''
        }
    
    blogName = ''
    owner=''
    def get(self):
        if users.get_current_user():
            self.blogName = self.request.get('blogName')
            self.context['welcome']=('Author: '+str(users.get_current_user()))
            if self.blogName!='':
              blogName = self.request.get('blogName')
              postTitle = self.request.get('title')
              owner = self.request.get('owner')
              queryBlog = BlogEntry.query(BlogEntry.blogName==blogName,BlogEntry.owner==owner)
              blogObject = queryBlog.get()
              parent_key = createKeyForBlog(blogObject.blogName,blogObject.owner,str(blogObject.date))
              query = PostEntry.query(PostEntry.title==postTitle,ancestor=parent_key)
              post = query.get()
              self.context['title'] = post.title
              self.context['content'] = post.content
              self.context['blogName'] = self.blogName
              self.context['display_selection'] = 'display:none'
              self.context['display_form'] = 'display:inline'
              self.context['fromWhere'] = 'definedBlog'
              self.context['update'] = '?update=true'
              self.response.write('update post')
            else:
              self.response.write('new post')
              query = BlogEntry.query(BlogEntry.owner==str(users.get_current_user()))
              if query.count()>0:
                self.context['blogName'] = 'Choose Blog to Write Post: '
                self.context['display_selection'] = 'display:inline'
                self.context['display_form'] = 'display:inline'
                self.context['blogs'] = query
                self.context['fromWhere'] = 'selection'
                self.context['title'] = 'default title'
                self.context['content'] = 'default content'
                self.context['update'] = ''
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

        title = cgi.escape(self.request.get('title'))
        content = cgi.escape(self.request.get('content'))
        owner = str(users.get_current_user())
        update = self.request.get('update')
        #img add
        #img = self.request.get('img')

        post = None
        
        if update=='true':
          previousTitle = self.request.get('title')
          queryBlog = BlogEntry.query(BlogEntry.blogName==blog,BlogEntry.owner==owner)
          blogObject = queryBlog.get()
          parent_key = createKeyForBlog(blogObject.blogName,blogObject.owner,str(blogObject.date))
          #query = PostEntry.query(PostEntry.title==previousTitle,ancestor=parent_key)
          query = PostEntry.query(PostEntry.title==previousTitle,PostEntry.blogName==blog,PostEntry.owner==owner)
          post = query.get()
          
        else:
          queryBlog = BlogEntry.query(BlogEntry.blogName==blog,BlogEntry.owner==owner)
          blogObject = queryBlog.get()
          parent_key = createKeyForBlog(blogObject.blogName,blogObject.owner,str(blogObject.date))          
          post = PostEntry(parent=parent_key)
          #query = PostEntry.query(PostEntry.title==title,PostEntry.blogName==blog,PostEntry.owner==owner)
          post.date = datetime.now()
          post.blogName = blog
          post.owner = owner

        #image add
        #if img!='':
        #  post.img = img
        
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
    'owner' : '',
    'tagorblog' : '',
    }


  def createViewPosts(self,query):
    viewPosts=[]
    for post in query:
      tmp = ViewPost(post.blogName,post.owner,post.title,post.content,post.date,post.modifydate,post.tags)
      viewPosts.append(tmp)
    return viewPosts
  
  def get(self):
    
    if users.get_current_user():
      self.context['display_user_panel'] = 'inline'
    else:
      self.context['display_user_panel'] = 'none'
    tagFlag = True
    pageNo = '1'
    tag=''
    self.context['page']=pageNo

    if self.request.get('tag')=='':
      blogName = self.request.get('blogName')
      owner = self.request.get('owner')
      self.context['nextblogName'] = 'blogName='+blogName
      self.context['nextowner'] = '&owner='+owner
      queryBlog = BlogEntry.query(BlogEntry.blogName==blogName,BlogEntry.owner==owner)
      blogObject = queryBlog.get()
      parent_key = createKeyForBlog(blogObject.blogName,blogObject.owner,str(blogObject.date))
      query = PostEntry.query(ancestor=parent_key).order(-PostEntry.date)
      tagFlag=False
      #f10 add
      self.context['tagorblog'] = 'Blog: '+blogName
      self.context['display_rss'] ='inline'
    else:
      tagFlag=True
      tag = self.request.get('tag')
      self.context['tagorblog'] = 'Tag: '+tag
      #f10 add
      self.context['display_rss'] ='none'
      query = PostEntry.query(PostEntry.tags==tag).order(-PostEntry.date)



   
    postList=[]
    
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

    viewPosts= self.createViewPosts(postList)

    httpList=[]
    imgList=[]
    viewcontent=''
    for viewpost in viewPosts:
      viewcontent = viewpost.content
      httpList = re.findall(r'http[s]?://.*\s|http[s]?://[^\s]*$',viewcontent)
      imgList = re.findall(r'http[s]?://[^\s]*?\.(?:jpg|png|gif)',viewcontent)
    
      for img in imgList:
        viewcontent = viewcontent.replace(img,'<img style = "display:inline" src="'+img+'"/ alt="'+img+'">')
      
      for h in httpList:
        if h not in imgList:
          viewcontent = viewcontent.replace(h,'<a href="'+h+'">'+h.strip()+'</a>')
      viewpost.content = viewcontent


    self.context['posts'] = viewPosts

    if users.get_current_user() and not tagFlag and str(users.get_current_user())== owner:
      self.context['display_edit'] = 'inline'
    else:
      self.context['display_edit'] = 'none'

    if tagFlag:
      self.context['tagPageNext'] = '&tag='+tag
    self.response.write('page no is 1</br>'+'query count = '+str(query.count())+'</br>')
    self.response.write(template.render(os.path.join(os.path.dirname(__file__),'viewBlog.html'),self.context))



  def post(self):
    if users.get_current_user():
      self.context['display_user_panel'] = 'inline'
    else:
      self.context['display_user_panel'] = 'none'

    pageNo = cgi.escape(self.request.get('pageno'))
    if self.request.get('tag')=='':
      blogName = self.request.get('blogName')
      owner = self.request.get('owner')
      self.context['blogName'] = blogName
      self.context['owner'] = owner
      self.context['nextblogName'] = 'blogName='+blogName
      self.context['nextowner'] = '&owner='+owner
      queryBlog = BlogEntry.query(BlogEntry.blogName==blogName,BlogEntry.owner==owner)
      blogObject = queryBlog.get()
      parent_key = createKeyForBlog(blogObject.blogName,blogObject.owner,str(blogObject.date))
      query = PostEntry.query(ancestor=parent_key).order(-PostEntry.date)
      tagFlag=False
      #f10 add
      self.context['display_rss'] ='inline'
    else:
      tagFlag=True
      #f10 add
      self.context['display_rss'] ='none'
      tag = self.request.get('tag')
      query = PostEntry.query(PostEntry.tags==tag).order(-PostEntry.date)

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
      
    viewPosts=self.createViewPosts(postList)


    httpList=[]
    imgList=[]
    viewcontent=''
    for viewpost in viewPosts:
      viewcontent = viewpost.content
      httpList = re.findall(r'http[s]?://.*\s|http[s]?://[^\s]*$',viewcontent)
      imgList = re.findall(r'http[s]?://[^\s]*?\.(?:jpg|png|gif)',viewcontent)
    
      for img in imgList:
        viewcontent = viewcontent.replace(img,'<img style = "display:inline" src="'+img+'"/ alt="'+img+'">')
      
      for h in httpList:
        if h not in imgList:
          viewcontent = viewcontent.replace(h,'<a href="'+h+'">'+h.strip()+'</a>')
      viewpost.content = viewcontent
   
    self.context['posts'] = viewPosts
    self.context['page'] = str(p)
    if users.get_current_user() and not tagFlag and str(users.get_current_user())== owner:
      self.context['display_edit'] = 'inline'
    else:
      self.context['display_edit'] = 'none'      
    self.response.write(template.render(os.path.join(os.path.dirname(__file__),'viewBlog.html'),self.context))

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
    content = post.content


    httpList = re.findall(r'http[s]?://.*\s|http[s]?://[^\s]*$',content)
    imgList = re.findall(r'http[s]?://[^\s]*?\.(?:jpg|png|gif)',content)

    for img in imgList:
      content = content.replace(img,'<img style = "display:inline" src="'+img+'"/ alt="'+img+'">')
      
    for h in httpList:
      if h not in imgList:
        content = content.replace(h,'<a href="'+h+'">'+h.strip()+'</a>')
    
    context['post'] = post
    context['postContent'] = content
    self.response.write(template.render(os.path.join(os.path.dirname(__file__),'viewPost.html'),context))     


class addTagHandler(webapp2.RequestHandler):
  context = {
    'display1' : 'inline',
    'display2' : 'inline',
    'blogName' : '',
    'owner' : '',
    'title' : '',
    }
  def get(self):
    blogName = self.request.get('blogName')
    postTitle = self.request.get('title')
    owner = self.request.get('owner')
    queryBlog = BlogEntry.query(BlogEntry.blogName==blogName,BlogEntry.owner==owner)
    blogObject = queryBlog.get()
    parent_key = createKeyForBlog(blogObject.blogName,blogObject.owner,str(blogObject.date))
    query = PostEntry.query(PostEntry.title==postTitle,ancestor=parent_key)
    post = query.get()
    self.context['blogName'] = blogName
    self.context['owner'] = owner
    self.context['title'] = postTitle
    self.context['display1'] = 'inline'
    self.context['display2'] = 'none'
    self.response.write(template.render(os.path.join(os.path.dirname(__file__),'addTag.html'),self.context))     

  def post(self):
    blogName = cgi.escape(self.request.get('blogName'))
    postTitle = cgi.escape(self.request.get('title'))
    owner = cgi.escape(self.request.get('owner'))
    tag = cgi.escape(self.request.get('tag'))
    queryBlog = BlogEntry.query(BlogEntry.blogName==blogName,BlogEntry.owner==owner)
    blogObject = queryBlog.get()
    parent_key = createKeyForBlog(blogObject.blogName,blogObject.owner,str(blogObject.date))
    query = PostEntry.query(PostEntry.title==postTitle,ancestor=parent_key)
    post = query.get()
    tagList = post.tags
    tagList.append(tag)
    post.tags = tagList
    post.put()
    
    self.context['display1'] = 'none'
    self.context['display2'] = 'inline'
    self.context['tag'] = tag
    self.context['title'] = postTitle
    self.context['tags'] = post.tags
    self.response.write(template.render(os.path.join(os.path.dirname(__file__),'addTag.html'),self.context))     

class uploadImageHandler(webapp2.RequestHandler):
  def get(self):    
    self.response.out.write("""
          <a href = "/">return to home page</a></br>
          <form action="/uploadImage" enctype="multipart/form-data" method="post">
            <div><label>Choose file to upload:</label></div>
            <div><input type="file" name="img"/></div>
            <div><input type="submit" value="Upload"></div>
          </form>
        </body>
      </html>""")

  def post(self):
    #img = self.request.get("img")
    img = images.resize(self.request.get('img'), 500, 500)
    imageEntity = ImageEntry()
    imageEntity.image = img
    imageEntity.put()
    url = self.request.url
    path = self.request.path
    l = len(url) - len(path)
    url = url[:l]
    imageEntity.permalink = url+'/image?key='+str(imageEntity.key.id())+'.png'
    imageEntity.put()
    self.response.write('<a href = "/"> return to home page</a></br>')
    self.response.write('use the link to reference uploaded image: '+imageEntity.permalink)
    
    
  
class viewImageHandler(webapp2.RequestHandler):
  def get(self):
    keystr = self.request.get('key')
    keyId = keystr.split('.')[0]
    key = ndb.Key(ImageEntry,long(keyId))
    img = key.get()
    if img != None:
      self.response.headers['Content-Type'] = "image/png"
      self.response.out.write(img.image)
    else:
      self.response.out.write('Image does not exist')

class rssHandler(webapp2.RequestHandler):
  def get(self):
    blogName = self.request.get('blogName')
    owner = self.request.get('owner')
    blog = BlogEntry.query(BlogEntry.blogName==blogName,BlogEntry.owner==owner).get()
    query = PostEntry.query(PostEntry.blogName==blogName,PostEntry.owner==owner)

    if blog == None:
      self.response.write('No such blog')
    else:
      xmlContent = ''' <?xml version="1.0" encoding="UTF-8"?>
                  <?xml-stylesheet type="text/xsl" href="/css/rss_xml_style.css"?>
                  <rss version="2.0">
                  <blog>
                    <blogName>'''+blog.blogName+'</blogName>'+'''
                    <owner>'''+blog.owner+'</owner>'+'''
                    <date>'''+str(blog.date)+'</date>'
      for post in query:
        xmlContent = xmlContent +'''
                    <post>
                      <modifydate>'''+str(post.modifydate)+'</modifydate>'+'''
                      <title>'''+post.title+'</title>'+'''
                      <createdate>'''+str(post.date)+'</createdate>'+'''
                      <content>'''+str(post.content)+'</content>'
        for tag in post.tags:
          xmlContent = xmlContent + '<tag>'+tag+'</tag>'
      
      xmlContent = xmlContent + '</post>'


    xmlContent = xmlContent + '</blog>'  
    self.response.headers['Content-Type'] = 'text/xml'
    self.response.write(xmlContent)

  

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/createBlog', createBlogHandler),
    ('/writePost',writePostHandler),
    ('/manageBlog',manageBlogHandler),
    ('/viewPost',viewPostHandler),
    ('/viewBlog',viewBlogHandler),
    ('/addTag',addTagHandler),
    ('/uploadImage',uploadImageHandler),
    ('/image',viewImageHandler),
    ('/rss',rssHandler),
], debug=True)
