import functools
import inspect
import datetime
import time

from json import dumps, loads

class InvalidDecoratorApplication(Exception):
	error_messages = {
	"en": {"message": "Decorator applied to a class, expected a function.", "location": {}},
	"ru": {"message": "Декоратор применен к классу, ожидалась функция.", "location": {}}
	}
	langs = ["en", "ru"]
	def __init__(self, name_class:str, lang="en"):
		if not lang in self.langs: lang = "en"
		self.message = self.error_messages[lang]
		for frame in inspect.getouterframes(inspect.currentframe()):
			if frame.function == "<module>" and frame.code_context is None:
				self.message["location"] = {"frame": frame.frame, "filename": frame.filename, "line": frame.lineno,"position": frame.positions, "function": frame.function, "name_class_error": name_class}
		super().__init__(self.message)
		
		
class Correction:
	
	def __init__(self, method: str):
		self.method = method
	
	def validator_type(self, params_name: list = "all"):
		if not isinstance(params_name, list) and not params_name == "all":
			raise TypeError(f"The params_name type must be list but not {params_name.__class__.__name__}.")
		def decorator(func):
			if inspect.isclass(func):
				raise InvalidDecoratorApplication(func.__name__)
			@functools.wraps(func)
			def validator(*args, **kwargs):
				annotations = func.__annotations__
				varnames = [value for value in func.__code__.co_varnames if not value == "self"]
				defaults = [] if func.__defaults__ is None else func.__defaults__
				default_values = dict(zip(varnames, defaults))
				vardata = inspect.getcallargs(func, *args, **kwargs)
				for varname, annotation in annotations.items():
					if params_name == "all" and not varname == "return":
						if not isinstance(vardata.get(varname), annotation) and not vardata.get(varname) == default_values.get(varname):
							raise TypeError(f"The {varname} type must be {annotation.__name__} but not {vardata.get(varname).__class__.__name__}.")
					elif not varname == "return":
						if not isinstance(vardata.get(varname), annotation) and varname in params_name and not vardata.get(varname) == default_values.get(varname):
							raise TypeError(f"The {varname} type must be {annotation.__name__} but not {vardata.get(varname).__class__.__name__}.")
				return func(*args, **kwargs)
			return validator
		return decorator
		
	@staticmethod
	def _correction_profile(response: dict) -> dict:
		time_get_info = time.strftime("%Y.%m.%d %X")
		platforms = {
		0: "Unknown",
		1: "Mobile version", 
		2: "IPhone", 
		3: "IPad", 
		4: "Android", 
		5: "Windows Phone", 
		6: "Windows 10", 
		7: "Full version site"
		}
		sexs = {
		0: "Unknown",
		1: "Woman", 
		2: "Man"
		}
		onlines = {
		0: "Offline",
		1: "Online",
		2: "Unknown"
		}
		platform = platforms[response.get("last_seen", {}).get("platform", 0)]
		last_time = response.get("last_seen", "Unknown")		
		if not last_time == "Unknown":
			last_time = datetime.datetime.fromtimestamp(last_time.get("time"))
			last_time = last_time.strftime("%Y.%m.%d %X")
		
		response["last_seen"] = {"platform": platform, "time": last_time}
		
		sex = sexs[int(response.get("sex", 0))]
		
		response["sex"] = sex
		
		online = onlines[response.get("online", 2)]
		response["online"] = online
		
		is_closed = response.get("is_closed", "Unknown")
		if not is_closed == "Unknown":
			if is_closed == 0: is_closed = "Open"
			elif is_closed == 1: is_closed = "Private"
		response["is_closed"] = is_closed
		
		domain = response.get("domain", "Unknown")
		if not domain == "Unknown":
			domain = "https://vk.com/{}".format(domain)
		response["domain"] = domain
		verified = response.get("verified", "Unknown")
		response["verified"] = verified
		response["now"] = time_get_info
		response.update({"last_seen": {"platform": platform, "time": last_time}, "sex": sex, "online": online, "is_closed": is_closed, "domain": domain, "verified": verified, "now": time_get_info})
		return loads(dumps(response))	 
	
	@staticmethod
	def _correction_wall(data: dict):
		count = data["count"]
		post_data = []
		for post in data["items"]:
			post_id = post.get("id", 0)
			owner_id = post.get("owner_id", 0)
			post_link = f"https://vk.com/wall{owner_id}_{post_id}"
			likes = post.get("likes", {}).get("count", 0)
			reposts = post.get("reposts", {}).get("count", 0)
			text = post.get("text", "")
			views = post.get("views", {}).get("count", 0)
			comments = post.get("comments", {}).get("count", 0)
			type = post["type"]
			date = datetime.datetime.fromtimestamp(post.get("date", time.time()))
			date = date.strftime("%Y.%m.%d %X")
			photos = []
			sizes = []
			size = post.get("attachments", {})
			for siz in size:
				siz = siz.get("photo", {})
				sizes.append(siz.get("sizes", []))
			if len(sizes) > 0:
				for photo_sizes in sizes[0]:
					photos.append((photo_sizes.get("height", 0), photo_sizes.get("width", 0), photo_sizes.get("url")))
			post_data.append({"post_id": post_id, "owner_id": owner_id, "link": post_link, "likes": likes, "reposts": reposts, "text": text, "views": views, "comments": comments, "photos": photos, "type": type, "date": date})
		return post_data
	