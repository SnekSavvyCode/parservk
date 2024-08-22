import grequests

from random import shuffle

from .correctionclass import Correction
from .models import VKApi
from .logger import LOGGER

_CORRECTION_MODEL = Correction(None)

class BaseClass:
	URL_API = "https://api.vk.com/method/"
	
	BASE_DICT = {"url": str, "methods": list[str], "name_attr": list[str], "name": str}
	
	_method_groups = {
	"url": f"{URL_API}groups", 
	"methods": [".getById", ".getMembers", ".isMember"],
	"name_attr": ["group_ids", "user_ids"],
	"name": "groups"
	}
	_method_users = {
	"url": f"{URL_API}users", 
	"methods": [".get", ".getSubscriptions", ".getFollowers"],
	"name_attr": ["user_ids"], 
	"name": "users"
	}
	_method_friends = {
	"url": f"{URL_API}friends", 
	"methods": [".get"], 
	"name_attr": ["user_ids"],
	"name": "friends"
	}
	_method_walls = {	
	"url": f"{URL_API}wall",
	"methods": [".get"],
	"name_attr": ["owner_ids"],
	"name": "walls"
	}
	
	MAX_COUNT = {
	"USERS": {"user_ids": 1000}, "GROUPS": {"group_ids": 500, "user_ids": 500}, 
	"FRIENDS": {"user_ids": None}, "WALLS": {"user_ids": 1}
	}
	
	_methods = {
	"GROUPS": _method_groups, "USERS": _method_users, 
	"FRIENDS": _method_friends, "WALLS": _method_walls
	}
	
	config = {
	"LOGGER": LOGGER
	}
	
	@_CORRECTION_MODEL.validator_type()
	def __init__(self, data: VKApi) -> None:
		if not isinstance(data.headers, dict):
			raise ValueError("The headers must be of the dict type.")
		self._LOGGER = self.config["LOGGER"]
		self.tokens = data.tokens
		self.v = data.v_api
		self.headers = data.headers
		self.proxies = data.proxies
	
	@staticmethod
	def _valid_users(users: list, max: int) -> list:
		if len(users) > max:
			return [users[step:step+max] for step in range(0, len(users)+1, max)]
		elif 1 <= len(users) <= max:
			return ", ".join(map(str, users))
			
	
	@classmethod
	def _valid_method(cls, method: str) -> dict:
		if not method in cls._methods:
			raise ValueError("method is not valid")
		return cls._methods[method]
	
	@_CORRECTION_MODEL.validator_type()
	def _valid_data(self, users_list: list, params: dict, method: str, name_methods: str, **kwargs):
			data_method = self._valid_method(method.upper())
			if not name_methods in data_method["methods"]:
				raise AttributeError(f"The method {name_methods} was not found in {data_method['methods']}.")
			name_attr = kwargs.get("name_attr")
			if not name_attr in data_method["name_attr"] and not name_attr is None:
				raise ValueError("not method in dict data")
			if name_attr is None: name_attr = data_method["name_attr"][0]
			max_count = self.MAX_COUNT[method.upper()].get(name_attr)
			data = self._valid_users(users_list, max_count)
			url = data_method["url"] + name_methods
					
			if isinstance(data, list):
				new_params = []
				for list_data in data:
					shuffle(self.tokens)
					params.update(self.headers)
					params.update({name_attr: ", ".join(map(str, list_data)), "access_token": self.tokens[0]})
					new_params.append(params.copy())
				response = [grequests.post(url, data=params) for params in new_params]
				return response
			else:
				shuffle(self.tokens)
				params.update(self.headers)
				params.update({name_attr: data, "access_token": self.tokens[0]})
				return (url, params)
				

	def method_info(self, method: str) -> dict:
		data = self._valid_method(method.upper())
		return data