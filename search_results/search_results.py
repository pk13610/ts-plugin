
import sublime, sublime_plugin


class StatusMessage:
	def __init__(self, view):
		self.view = view

	def message(self, msg):
		self.view.set_status('search_results_msg', msg)
		sublime.set_timeout(self.clear, 3000)

	def clear(self):
		self.view.set_status('search_results_msg', '')

class search_results(sublime_plugin.TextCommand):

	def run(self, edit):
		self.msg = StatusMessage(self.view)
		self.view.window().show_input_panel(
			u"Seach", 
			self.view.substr(self.view.sel()[0]), 
			self.on_goto_selected_item, 
			self.on_selection_changed, 
			self.on_cancel
		)
		self.msg.clear()

	def on_goto_selected_item(self, s):
		self.msg.clear()
		self.results = self.view.find_all(s, 0)
		if len(self.results) == 0:
			self.view.window().show_input_panel(
				u"Seach", 
				s, 
				self.on_goto_selected_item, 
				self.on_selection_changed, 
				self.on_cancel
			)
			self.msg.message('Not Found')
			return
		else:
			results = ['<Copy>']
		for l in self.results:
			line_num = int(self.view.rowcol(l.a)[0]) + 1
			line_str = self.view.substr(self.view.line(l))
			results.append("%5d  %s" % (line_num, line_str))

		self.msg.message("Found %d" % len(self.results))
		self.view.window().show_quick_panel(
			results,
			self.on_sel_panle_done
		)

	def on_sel_panle_done(self, i):
		if i == -1:
			pass
		elif i == 0:
			content = ""
			for r in self.results:
				content += "%s    %s\n" % (r, self.view.substr(self.view.line(r)) )
			sublime.set_clipboard(content)
		else:
			self.view.sel().clear()
			self.view.show(self.results[i-1])
			self.view.sel().add(self.results[i-1])

	def on_selection_changed(self, input):
		pass

	def on_cancel(self):
		pass

	def __del__(self):
		if hasattr(self, 'msg') and self.msg:
			print '__del__'
			self.msg.clear()


