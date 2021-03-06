# -*- coding: utf-8 -*-

import time
import os
import subprocess
import codecs
import sys

NAME_FORMATE = r'%s-%s.md'

HEAD_FORMATE="""
---
layout: post
tagline: %s
category: %s
tags: [%s]
---
{%% include JB/setup %%}
%s
"""

def  add_head(content,  tagline="", category="post",  tags=[]):
    tags_str = ''
    i = len(tags)
    for tag in tags:
        tags += tag
        i -= 1
        if i > 0:
            tags += ','
        else:
            break
    new_content = HEAD_FORMATE % (tagline, category, tags_str, content)
    return new_content

def formate_name(path, name):
    pos = 1
    tmp  = name
    print name 
    print path
    while True:
        files = os.listdir(path)
        if tmp in files:
            i = name.rfind('.')
            tmp = name[:i] + '-(%d)' % pos + name[i:]
            pos += 1
        else:
            return tmp

def execute_cmd(path, cmd):
    out, err = "", ""
    try:
        print u"Execute: " + cmd
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=path
        )
        out, err = proc.communicate()
        if out and out != "":
            print out
        if err and err != "":
            print err
    except Exception as e:
        return False, out, err
    return True, out, err

def git_commit_push(path, fname):
    cmd_add = u"git add ./" +  fname
    cmd_commit = u'git commit -m  "auto-add %s" ' % fname +  fname
    cmd_push = u"git push "

    result, out, err = execute_cmd(path, cmd_add)
    if not result: return out, err
    result, out, err = execute_cmd(path, cmd_commit)
    if not result: return out, err
    result, out, err = execute_cmd(path, cmd_push)
    return out, err

import threading

class ThreadClass(threading.Thread):
    def run(self):
        date_str = time.strftime('%Y-%m-%d', time.localtime())
        new_title = self.title.strip().replace(' ', '-')
        name = NAME_FORMATE % (date_str, new_title)
        new_content = add_head(self.content, self.category,  self.tagline,  self.tags)
        new_name = formate_name(self.path, name)

        file_name = os.path.join(self.path, new_name)
        if not os.path.isdir(self.path) :
            os.mkdir(self.path)
        codecs.open(file_name, 'w', encoding='utf-8').write(new_content)
        print git_commit_push(self.path, new_name)

    def save2_github_path(self, path, title, content, category="", tagline="", tags=[]):
        self.path = path
        self.title = title
        self.content = content
        self.category = category
        self.tagline = tagline
        self.tags = tags
        self.setDaemon(True)
        self.start()

def save2_github_path(path, title, content, category="", tagline="", tags=[]):
    __git_thread = ThreadClass()
    __git_thread.save2_github_path(path, title, content, category, tagline, tags)


test_path='D:\code\github\pk13610.github.com\_posts'
test_title = u"标题"
test_content = u"我试验"

print save2_github_path(test_path, test_title, test_content, tags=['douban'])

