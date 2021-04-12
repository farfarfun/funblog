#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/04/29 19:31
# @Author  : niuliangtao
# @Site    : 
# @File    : blog2.py
# @Software: PyCharm

# !/usr/bin/python2
"""
This script mainly intend for uploading local Html file to blog site using metaWeblog API.
Usages:
./blog.py post post.[org|adoc|html]
./blog.py list
./blog.py delete post-id
"""
import os
import os.path

base_dir = os.path.dirname(os.path.abspath(__file__))

from xmlrpc.client import ServerProxy, Binary
import re
import mimetypes
import os.path
import hashlib
from subprocess import Popen, PIPE, STDOUT


def read(path):
    try:
        with open(path) as f:
            return f.read()
    except IOError:
        return ''


def write(path, content):
    with open(path, 'w') as f:
        f.write(content)


def popen(cmd):
    return Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT).communicate()[0]


def to_html(path, target):
    def mv(src, target):
        return popen('mv %s %s' % (src, target))

    def chext(path, ext):
        return re.sub(r'(\.[^/.]*)$', ext, path)

    def get_ext(name):
        index = name.rfind('.')
        if index == -1: return ""
        return name[index + 1:].lower()

    def org2html(src, target):
        cmd = """emacs --batch --execute '(require `org)' --visit=%s --execute
'(progn (setq org-export-headline-levels 2)
(setq org-export-html-postamble "") (setq org-export-html-preamble "")
(setq org-export-htmlize-output-type `css)
(setq org-export-html-style "<link rel=\\"stylesheet\\" type=\\"text/css\\" href=\\"org.css\\">")
(org-export-as-html-batch))'"""
        output = popen(cmd.replace('\n', ' ') % src)
        mv(chext(src, '.html'), target)
        return output

    def html2html(src, target):
        return mv(src, target)

    def adoc2html(src, target):
        return popen('asciidoc %s -o %s' % (src, target))

    handlers = dict(htm=html2html, html=html2html, adoc=adoc2html, asciidoc=adoc2html, org=org2html)
    f = handlers.get(get_ext(path))
    if not f: raise Exception('do not know how to make html from %s' % path)
    return f(path, target)


def mkfile(src, target, handler):
    def md5(str):
        return hashlib.md5(str).hexdigest()

    def is_updated(path, md5_file):
        return md5(read(path)) != read(md5_file)

    dep = target + '.dep'
    if is_updated(src, dep):
        handler(src, target)
        write(dep, md5(read(src)))
    return read(target)


def cached_call(f, src):
    def mkdir(dir):
        if not os.path.exists(dir): os.mkdir(dir)

    cache_dir = os.path.join(base_dir, '.cache')
    mkdir(cache_dir)
    result = os.path.join(cache_dir, (src + '.' + f.func_name).replace('/', '!'))

    def handler(src, target):
        return write(target, f(src))

    return mkfile(src, result, handler)


def resolve_local_ref(content, upload, base_dir):
    'I would not to deal with uppercase tags'

    def realpath(path):
        return re.match('^([a-z]+:)?/', path) and path or os.path.join(base_dir, path)

    def url(path):
        print
        'upload(%s)' % (repr(path))
        return os.path.exists(path) and upload(path)['url'] or path

    def new_img(m):
        return '<img src="%s" %s/>' % (cached_call(url, realpath(m.group(1))), m.group(2))

    def new_archor(m):
        return '<a href="%s" %s>' % (cached_call(url, realpath(m.group(1))), m.group(2))

    def resolve_img_ref(content):
        return re.sub('<img\s+src\s*=\s*"(.*?)"(.*?)/>', new_img, content)

    def resolve_archor_ref(content):
        return re.sub('<a\s+href\s*=\s*"(.*?)"(.*?)>', new_archor, content)

    return resolve_archor_ref(resolve_img_ref(content))


class MetaWeblog:
    '''works with www.cnblogs.com atleast'''

    def __init__(self, serviceUrl, appKey, usr, passwd):
        self.serviceUrl, self.appKey, self.usr, self.passwd = serviceUrl, appKey, usr, passwd
        self.server = ServerProxy(self.serviceUrl)

    def getUsersBlogs(self):
        return self.server.blogger.getUsersBlogs(self.appKey, self.usr, self.passwd)

    def getCategories(self, blogid=''):
        return self.server.metaWeblog.getCategories(blogid, self.usr, self.passwd)

    def getRecentPosts(self, count=5, blogid=''):
        return self.server.metaWeblog.getRecentPosts(blogid, self.usr, self.passwd, count)

    def deletePost(self, id):
        return self.server.blogger.deletePost(self.appKey, id, self.usr, self.passwd, False)

    def getPost(self, id):
        return self.server.metaWeblog.getPost(id, self.usr, self.passwd)

    def newPost(self, title='Title used for test', description='this is a test post.', category='no category',
                publish=True, blogid='', **kw):
        return self.server.metaWeblog.newPost(blogid, self.usr, self.passwd,
                                              dict(kw, title=title, description=description, category=category),
                                              publish)

    def editPost(self, id, title='Title used for test', description='this is a test post.', category='no category',
                 publish=True, **kw):
        return self.server.metaWeblog.editPost(id, self.usr, self.passwd,
                                               dict(kw, title=title, description=description, category=category),
                                               publish)

    def newMediaObject(self, path, name=None, blogid=''):
        with open(os.path.expanduser(path)) as f:
            content = Binary(f.read())
        type, _ = mimetypes.guess_type(path)
        name = name or os.path.basename(path)
        return self.server.metaWeblog.newMediaObject(blogid, self.usr, self.passwd,
                                                     dict(name=name, type=type, bits=content))

    def post(self, path):
        def get_tagged_body(html, tag):
            tag_re = '%s|%s' % (tag.lower(), tag.upper())
            m = re.search('<(?:%s)>(.*?)</(?:%s)>' % (tag_re, tag_re), html, re.S)
            return m and m.group(1)

        def chext(path, ext):
            return re.sub(r'(\.[^/.]*)$', ext, path)

        html = chext(path, '.html')
        print(to_html(path, html))
        content = read(html)
        title = get_tagged_body(content, 'title') or 'Default Title'
        description = resolve_local_ref(get_tagged_body(content, 'body') or content, self.newMediaObject,
                                        os.path.dirname(os.path.realpath(path)))
        matched = filter(lambda p: p['title'] == title.decode('utf-8'), self.getRecentPosts(10))
        if matched:
            return self.editPost(matched[0]['postid'], title, description)
        else:
            return self.newPost(title, description)

    def list(self, count=10):
        for p in self.getRecentPosts(count):
            # print '-' * 80
            # print '#%(postid)s\t%(title)s\n%(description).80s'%p
            print('%(postid)s\t%(title)s' % p)

    def delete(self, id):
        return self.deletePost(id)

    def __repr__(self):
        return 'MetaWeblog(%s, %s, %s)' % (repr(self.serviceUrl), repr(self.usr), repr(self.passwd))


if __name__ == '__main__':
    serviceUrl, appKey = 'https://rpc.cnblogs.com/metaweblog/bingtao', '1007530194'

    blog = MetaWeblog(serviceUrl, appKey, usr, passwd)

    blog.list(10)
