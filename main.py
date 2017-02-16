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
import webapp2
import os
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Blog(db.Model):
    blog_title = db.StringProperty(required = True)
    blog_content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    
    # ADD TO DATABASE EXAMPLE
    # a = ClassName(params)
    # a.put()
    
    # QUERY DATABASE EXAMPLE
    # a = db.GqlQuery("SELECT * FROM table")


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
        
        
class Index(Handler):       
        
    def get(self):
        # TODO: Extract all blog posts to a list, ordered by date created, most recent first.
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        # TODO: First five blog posts need to be listed here, most recent first.        
        #self.render("index.html", blogs)
        
        t = jinja_env.get_template('index.html')
        content = t.render(blogs = blogs)
        self.write(content)
        
        
class NewBlog(Handler):
    def get(self):
        error = ''
        t = jinja_env.get_template('new_blog_form.html')
        content = t.render(error = error)
        self.write(content)
        
    def post(self):
        error = {}
        is_errored = False
        
        
        blog_title = self.request.get("blog_title")
        blog_content = self.request.get("blog_content")
        
        if (blog_title and blog_content):
            blog = Blog(blog_title = blog_title, blog_content = blog_content)
            blog.put()
            self.redirect('/blog/%s' % blog.key().id())
        else:
            is_errored = True
            if not blog_title:
                error['title_error'] = 'You can ride through the web on a blog with no name, but not here.'
            if not blog_content:
                error['content_error'] = 'No one wants an empty package, write something!'
                
            t = jinja_env.get_template('new_blog_form.html')
            content = t.render(error = error, blog_title = blog_title, blog_content = blog_content)
            self.write(content)
        

class ViewPostHandler(Handler):
    def get(self, id):
        id = int(id)
        errors = {}
        blog = Blog.get_by_id(id)

        
        if not blog:
            errors['no_blog'] = 'There is no blog by that ID.'
            
        t = jinja_env.get_template('index.html') 
        content = t.render(errors = errors, blog = blog)
        self.write(content)
        
        
    
    
    
app = webapp2.WSGIApplication([
    ('/', Index),
    ('/new_blog', NewBlog),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
