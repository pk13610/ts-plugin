
import sublime

class Note4stSettings:
	def create(self):
		cfg = sublime.load_settings("note4st.sublime-settings")
		name = cfg.get("user")
		self.save_path = cfg.get("save_path")
		for user in cfg.get("user_list"):
			if name == user["user"]:
				self.password = user["password"]
				self.email = user["email"]
				self.json_path = user["json_path"]
				return self


