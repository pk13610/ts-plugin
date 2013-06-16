# -*- coding: utf-8  -*-

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))

import json
import sublime
import sublime_plugin
from note4st_settings import Note4stSettings
from send2_githubblog.send2_githubblog import save2_github_path
from douban.note4st_douban import Note4stDouban

SETTINGS = Note4stSettings().create()
DOUBAN = Note4stDouban(SETTINGS.json_path)


def LOGIN(user):
	if not user.is_login:
		try:
			user.login(None, None, user.user.token)
		except:
			sublime.error_message(u"Failed on login")
	return user.is_login

def MSG(view, msg, delay=3000):
	def clear_message():
		view.set_status('note4st', '')
	view.set_status('note4st', msg)
	sublime.set_timeout(clear_message, delay)

def GET_SEL_TEXT(view):
	content = view.substr(view.sel()[0])
	if len(content) <= 0:
		content = view.substr(sublime.Region(0, view.size()))
	return content

class Note4stNote(object):
	"""docstring for Note4stNote"""
	def __init__(self, note_type="douban"):
		super(Note4stNote, self).__init__()
		self.type = note_type
		self.id = -1
		self.title = ""
		self.sub_title = ""
		self.publish_time = ""
		self.content = ""
		self.note_url = ""
		self.privacy = ""

	def description(self):
		"""return description of note"""
		return [self.title, self.publish_time]

class ShowNoteList(object):
	""" list all notes by pages """

	def __init__(self, caller, user, callback):
		self.caller = caller
		self.view = caller.view
		self.user = user
		self.callback = callback
		self.notes = []
		self.display_list = []

	def show(self):
		if not LOGIN(self.user):
			return
		self.__show(0)

	def __show(self, start_count):
		notes = self.user.client.note.list(self.user.user.uid, start_count)
		count = int(notes["count"])
		start = int(notes["start"])
		total = int(notes["total"])
		self.notes = []
		self.display_list = []
		for note in notes["notes"]:
			try:
				nn = Note4stNote()
				nn.title = note['title']
				nn.content = note['content']
				nn.id = note['id']
				nn.publish_time = note['publish_time']
				nn.note_url = note['alt']
				nn.privacy = note['privacy']
				self.notes.append(nn)
				self.display_list.append(nn.description())
			except Exception as e:
				print e
		if start + count + 1 < total:
			self.last_count = start + count
			self.display_list.append(u"Next (%d)..." % (total - start - count))
		self.view.window().show_quick_panel(self.display_list, self.__callback)
		MSG(self.view, u"notes:%d--%d/%d" % (start+1, start+count, total))

	def __callback(self, i):
		if i>0 and i+1 > len(self.notes): # turn page
			self.__show(self.last_count)
		else:
			self.callback(self.notes, i)


########### note4st commands #########

class note4st(sublime_plugin.TextCommand):
	""" note4st command list """

	def run(self, edit):
		MSG(self.view, "##########")
		cmds = ["Send note", "Get notes", "Delete note"]
		self.view.window().show_quick_panel(cmds, self.on_done)

	def on_done(self, i):
		if i == -1:
			return
		cmds = ["note4st_send_note", "note4st_get_notes", "note4st_del_note"]
		self.view.run_command(cmds[i])


class note4st_send_note(sublime_plugin.TextCommand):
	""" note4st_send_note """

	def run(self, edit):
		if not LOGIN():
			return
		content = GET_SEL_TEXT(self.view)
		title = content[0:content.find('\n')]
		if sublime.ok_cancel_dialog(u"Send?\n'%s'" % title):
			self.view.window().show_input_panel(
				"Note title", 
				title,
				self.on_title_done, 
				self.void_callback, 
				self.void_callback
			)

	def on_title_done(self, title):
		try:
			MSG(self.view, u"sending note: %s" % title)
			content = self.view.substr(self.view.sel()[0])
			if len(content) == 0:
				content = self.view.substr(sublime.Region(0, self.view.size()))
			DOUBAN.client.note.new(title, content)
			if SETTINGS.save_path is not "":
				save2_github_path(SETTINGS.save_path, unicode(title), unicode(content), tags=['douban'])
			MSG(self.view, u"Done: %s" % title)
		except Exception as e:
			sublime.error_message(u"Error on sending '%s' \n\n %s" % (title, e))
			raise e

	def void_callback(self, s):
		pass


class note4st_get_notes(sublime_plugin.TextCommand):
	""" note4st_get_notes """

	def run(self, edit):
		if not LOGIN():
			return
		self.edit = edit
		ShowNoteList(self, DOUBAN, self.on_done).show()

	def on_done(self, notes, i):
		if i == -1:
			return
		new_view = self.view.window().new_file()
		new_view.set_name("%s_%s" % (notes[i].title, notes[i].publish_time))
		new_view.insert(self.edit, 0, notes[i].content)

class note4st_del_note(sublime_plugin.TextCommand):
	""" note4st_del_note """

	def run(self, edit):
		if not LOGIN():
			return
		self.edit = edit
		ShowNoteList(self, DOUBAN, self.on_done).show()

	def on_done(self, notes, i):
		if i == -1:
			return
		try:
			note = notes[i]
			if sublime.ok_cancel_dialog(u"Delete %s\n\n'%s'" % (note.publish_time, note.title)):
				DOUBAN.client.note.delete(note.id)
		except Exception as e:
			sublime.error_message(u"Error on delete '%s'" % (e))
			raise e

