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


def login():
	if not DOUBAN.is_login:
		try:
			DOUBAN.login(None, None, DOUBAN.user.token)
		except:
			sublime.error_message(u"Failed on login")

class note4st_helper:
	""" note4st interactive helper """

	def __init__(self, caller):
		self.caller = caller
		self.view = caller.view
		self.status_message_key = caller.__class__.__name__
		print self.status_message_key

	def message(self, msg, delay=3000):
		self.view.set_status(self.status_message_key, msg)
		sublime.set_timeout(self.clear_message, delay)

	def clear_message(self):
		self.view.set_status(self.status_message_key, '')

	def show_note_list(self, callback=None):
		login()
		self.id_list = []
		self.titles = []
		self.contents = []
		for note in DOUBAN.client.note.list(DOUBAN.user.uid)["notes"]:
			try:
				self.contents.append(note["content"])
				self.id_list.append(note[u'id'])
				self.titles.append([note[u"title"], note[u"update_time"]])
			except:
				print note
		self.view.window().show_quick_panel(self.titles, callback)
		self.helper.message(u"%s notes found" % int(len(self.titles)))

	def get_selected_text(self):
		content = self.view.substr(self.view.sel()[0])
		if len(content) <= 0:
			content = self.view.substr(sublime.Region(0, self.view.size()))
		return content

class note4st(sublime_plugin.TextCommand):
	""" note4st command list """

	def run(self, edit):
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
		self.helper = note4st_helper(self)
		content = self.helper.get_selected_text()
		title = content[0:content.find('\n')]
		if sublime.ok_cancel_dialog(u"Send?\n'%s'" % title):
			login()
			self.view.window().show_input_panel(
				"Note title", 
				title,
				self.on_title_done, 
				self.void_callback, 
				self.void_callback
			)

	def on_title_done(self, title):
		try:
			self.helper.message(u"sending note: %s" % title)
			content = self.view.substr(self.view.sel()[0])
			if len(content) == 0:
				content = self.view.substr(sublime.Region(0, self.view.size()))
			DOUBAN.client.note.new(title, content)
			if SETTINGS.save_path is not "":
				save2_github_path(SETTINGS.save_path, unicode(title), unicode(content), tags=['douban'])
			self.helper.message(u"Done: %s" % title)
		except Exception as e:
			sublime.error_message(u"Error on sending '%s' \n\n %s" % (title, e))
			raise e

	def void_callback(self, s):
		pass

class note4st_get_notes(sublime_plugin.TextCommand):
	""" note4st_get_notes """

	def run(self, edit):
		self.helper = note4st_helper(self)
		login()
		self.edit = edit
		self.helper.show_note_list(self.on_done)

	def on_done(self, i):
		if i == -1:
			return
		new_view = self.view.window().new_file()
		new_view.set_name("%s_%s" % (self.helper.titles[i][1], self.helper.titles[i][0]))
		new_view.insert(self.edit, 0, self.helper.contents[i])

class note4st_del_note(sublime_plugin.TextCommand):
	""" note4st_del_note """

	def run(self, edit):
		self.helper = note4st_helper(self)
		login()
		self.edit = edit
		self.helper.show_note_list(self.on_done)

	def on_done(self, i):
		if i == -1:
			return
		try:
			note_date = self.helper.titles[i][1]
			note_title = self.helper.titles[i][0]
			if sublime.ok_cancel_dialog(u"Delete %s\n\n'%s'" % (note_date, note_title)):
				DOUBAN.client.note.delete(self.helper.id_list[i])
		except Exception as e:
			sublime.error_message(u"Error on delete '%s'" % (e))
			raise e

