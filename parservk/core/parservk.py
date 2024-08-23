import grequests
import requests
import datetime
import time
import re
from random import shuffle
from json import dumps, loads, dump, load

from .baseclass import BaseClass, _CORRECTION_MODEL
from .correctionclass import Correction
from .models import VKApi, DataProfile, DataGroups, DataFriends, DataWalls, VERSION_API

TOKENS = ['vk1.a.Zi0sgk6hNRFSCZEafLX4q15E9FxFERgbIr1nrHChl_3wG59aAgJ2gjzq0YFHWUumha4iHALDTW7uNT1qQVBz8vLah5K8nu-Cks5YXAwie8dz_-WK6L95zeX35v_MePJTPFiqSAMin2ANIiQiNk7g-V8xl_EOZdmR1TpVawgxmxmrKH1s7GRc9ZOmm8W1fSvi', 'vk1.a.RuQO6_HiW-pwGtJWFEasSRGHqyUV2R-by-Y913PDxY71BPP2XmfJfbsnJUH5k3upV3kfa50-LZabe1P5UVXpxDyUE9Njz5oIFfeKC1JTkSrbmc2CuLysQznQ1ipvfZpaLdscKzdGCi90eOaD5RGoSfruRZyCZSDv7NrW4pTfCtg7JvVDVUM-cLNRFffKuIZR', 'vk1.a.4QjdrI3z5Vdvp1itlr15McNYHV4FKkvpHjKs6YwPr-yigMbM9VdT-iIhbpf2FC_MHJejSzkSJvWzH0g_qe-24OkhJzXDo8fe3jbeyevze02LRS8N6cs_RIAov_VrAVbqHeniE32HK7UxVoHaHbSKKiFx0sKrBOD9-mxI-qM5to2FsyTf5wWaJ3TlWhIXzLBt', 'vk1.a.uHdSySnm7PxaVEguf-11U5c4Mqw91PKmDw1mdqAC8D9XQiL3Ps5Hd1t9rDa-hFWGJf7Hn6isk3WoQD-8hDH9UjTI692EtahDHumsJZuRDgP44_XSWZN0LxoksalpaKvMFPORrS-HhsOJh0pv2zdHB0KfkQNICJudTYCZGzaoanxSKuOWsIFKX7uqUN7SrnH6']

HEADERS = {
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
			"Content-Type": "application/json",
}





class Profile(BaseClass):
	
	ERRORS = {"error_type": {}}
	
	FIELDS = "bdate, about, status, sex, domain, activities, books, city, country, contacts, photo_id, photo_max, nickname, schools, site, photo_50, photo_200, photo_100, photo_200_orig, photo_400_orig, verified, online, last_seen, quotes, relation, followers_count, career, counters, education, games, has_photo, home_town, interests, occupation, personal, screen_name, trending, tv, universities"
	
	_NAME = "USERS"
		
	def get_profile(self, data: DataProfile):
		start = time.time()
		if not isinstance(data, DataProfile):
			raise TypeError("data type is DataProfile")
		shuffle(self.tokens)
		user_id = data.user_id
		user_ids = data.user_ids
		subscriptions = data.subscriptions
		followers = data.followers
		wall = data.wall
		friends = data.friends
		data_method = self.method_info(self._NAME)
		method = data_method["methods"][0]
		url = f"{data_method['url']}{method}"
		param = {
		"access_token": self.tokens[0],
		"v": self.v,
		"fields": self.FIELDS
		}
		subscriptions_data = None
		friends_data = None
		followers_data = None
		wall_data = None
		if not user_ids is None:
			if not user_id is None: user_ids.append(user_id)
			data = self._valid_data(user_ids, param, self._NAME, method)
			if isinstance(data[0], grequests.AsyncRequest):
				result = grequests.map(data)
				users_data = []
				starts = []
				for response in result:
					if response and not "error" in response.json():
						response = response.json()["response"]
						for index in range(0, len(response)):
							respon = _CORRECTION_MODEL._correction_profile(response[index])
							users_data.append(loads(dumps({respon["id"]: {"profile": respon, "subscriptions": subscriptions_data, "wall": wall_data, "friends": friends_data}, "first_name": str(respon.get("first_name")), "last_name": str(respon.get("last_name")), "sex": respon["sex"], "platform": respon["last_seen"]["platform"], "domain": respon.get("domain", "Unknown")})))
					elif not response:
						self._LOGGER.warning(f"{response.url} status code {response.status_code}.")	
				return users_data
			else:
				respon = requests.post(data[0], data=data[1])
				if respon and not "error" in respon.json():
					responses = []
					response = respon.json()["response"]
					for index in range(0, len(response)):
						respon = _CORRECTION_MODEL._correction_profile(response[index])
						responses.append(loads(dumps({respon["id"]: {"profile": respon, "subscriptions": subscriptions_data, "followers": followers_data, "friends": friends_data}, "first_name": str(respon.get("first_name")), "last_name": str(respon.get("last_name")), "sex": respon["sex"], "platform": respon["last_seen"]["platform"], "domain": respon.get("domain", "Unknown")})))
					return responses
				elif not respon:
					self._LOGGER.warning(f"{respon.url} status code {respon.status_code}.")
		param.update({"user_id": user_id})
		response = requests.get(url, params=param, headers=self.headers)
		if response and not "error" in response.json() and response.json()["response"]:				
			response = _CORRECTION_MODEL._correction_profile(response.json()["response"][0])
			if subscriptions:
				subscriptions_data = self.get_connections(DataProfile(user_id=user_id, data_subscriptions=True),"subscriptions")
			if friends:
				friends_data = Friends(VKApi(self.tokens, self.v, self.headers, self.proxies)).get_friends(DataFriends(user_id=user_id, data_friends=True))
			if followers:
				followers_data = self.get_connections(DataProfile(user_id=user_id, data_followers=True),"followers")
			if wall:
				wall_data = Walls(VKApi(self.tokens, self.v, self.headers, self.proxies)).get_wall(DataWalls(owner_id=user_id))
			return loads(dumps({response["id"]: {"profile": response, "subscriptions": subscriptions_data, "followers": followers_data, "wall": wall_data, "friends": friends_data}, "first_name": str(response.get("first_name")), "last_name": str(response.get("last_name")), "sex": response["sex"], "platform": response["last_seen"]["platform"], "domain": response.get("domain", "Unknown")}))
	
	
	
	def get_connections(self, data: DataProfile, method: str = "subscriptions") -> dict:
		if not isinstance(data, DataProfile):
			raise TypeError("Data type is DataProfile")
		if not method.lower() in ["subscriptions", "followers"]:
			raise ValueError(f"Method {method} not found.")
		shuffle(self.tokens)
		user_id = data.user_id
		data_method = self.method_info(self._NAME)
		if method.lower() == "subscriptions": method_connection = data_method["methods"][1]
		else: method_connection = data_method["methods"][2]

		url = f"{data_method['url']}{method_connection}"
		data_sub = data.data_subscriptions
		data_followers = data.data_followers
		param = {
		"access_token": self.tokens[0],
		"v": self.v,
		"user_id": user_id
			}
		response = requests.get(url, params=param, headers=self.headers)
		if response and not "error" in response.json():
			response = response.json()["response"]
			data_users, data_groups = {"users": 0}, {"groups": 0}
			if data_sub and method.lower() == "subscriptions":
				count_users = response.get("users").get("count")
				count_groups = response.get("groups").get("count")
				if count_users == 1:
					data_users = self.get_profile(DataProfile(response.get("users").get("items")[0]))
				elif count_users > 1:
					data_users = self.get_profile(DataProfile(user_ids=response.get("users").get("items")))
	
				if count_groups == 1:
					data_groups = Groups(VKApi(self.tokens, self.v, self.headers, self.proxies)).get_group(DataGroups(group_id=response.get("users").get("items")[0]))
							
				elif count_groups > 1:
					data_groups = Groups(VKApi(self.tokens, self.v, self.headers, self.proxies)).get_group(DataGroups(group_ids=response.get("users").get("items")))
				return {"users": data_users, "groups": data_groups}
			
			elif data_followers and method.lower() == "followers":
				count_items = response["count"]
				if count_items == 1:
					data_followers = self.get_profile(DataProfile(response["items"][0]))
				elif count_items > 1:
					data_followers = self.get_profile(DataProfile(user_ids=response["items"]))
				return data_followers
			return response
		elif not response:
			self._LOGGER.warning(f"{response.url} status code {response.status_code}.")						
		return None

class Groups(BaseClass):
	
	FIELDS = "id, name, screen_name, is_closed, deactivated, type, photo_50, photo_100, photo_200, activity, 		addresses, age_limits, city,  contacts, counters, country, cover, crop_photo, description, has_photo, links, 	main_album_id, main_section, market, members_count, place, public_date_label, site, start_date, finish_date, 	status, trending, verified, wall, wiki_page"
	_NAME = "GROUPS"			
	
	def get_group(self, data: DataGroups):
		if not isinstance(data, DataGroups):
			raise TypeError("data type is DataGroups")
		shuffle(self.tokens)
		group_id = data.group_id
		group_ids = data.group_ids
		data_method = self.method_info(self._NAME)
		method = data_method["methods"][0]	
		param = {
		"access_token": self.tokens[0],
		"v": self.v,
		"fields": self.FIELDS
		}
		if not group_ids is None:
			if not group_id is None: group_ids.append(group_id)
			data = self._valid_data(group_ids, param, self._NAME, method, name_attr="group_ids")
			if isinstance(data, grequests.AsyncRequest):
				result =  grequests.map(data)
				group_data = []
				for data in result:
					if data and not "error" in data.json():
						group_data.append(data.json()["response"])
				return group_data
			response = requests.post(data[0], data=data[1], headers=self.headers)
			if response and not "error" in response.json():
				return response.json()["response"]
		url = f"{data_method['url']}{method}"
		param.update({"group_id": group_id})
		response = requests.get(url, params=param, headers=self.headers)
		if response and not "error" in response.json():
			return response.json()["response"]
		elif not response:
				self._LOGGER.warning(f"{response.url} status code {response.status_code}.")
		return None
	
	def get_ismember(self, data: DataGroups):
		if not isinstance(data, DataGroups):
			raise TypeError("data type is DataGroups")
		shuffle(self.tokens)
		group_id = data.group_id
		user_id = data.user_id
		user_ids = data.user_ids
		data_method = self.method_info(self._NAME)
		method = data_method["methods"][2]
		params = {
		"access_token": self.tokens[0],
		"group_id": group_id,
		"v": self.v,
		}
		if not user_ids is None:
			if not user_id is None: user_ids.append(user_id)
			data = self._valid_data(group_ids, params, self._NAME, method, "users_ids")
			if isinstance(data, grequests.AsyncRequest):
				result = grequests.map(data)
				group_data = []
				for data in result:
					if data:
						group_data.append(data.json())
				return group_data
			response = requests.post(data[0], data=data[1], headers=self.headers)
			if response:
				return response.json()
		url = f"{data_method['url']}{method}"
		params.update({"user_id": user_id})
		response = requests.get(url, params=params, headers=self.headers)
		if response and not "error" in response.json():
			return response.json()["response"]
		elif not response:
			self._LOGGER.warning(f"{response.url} status code {response.status_code}.")
		return None
					
	def get_members(self, data: DataGroups) -> dict:
		if not isinstance(data, DataGroups):
			raise TypeError("data type is DataGroups")
		shuffle(self.tokens)
		group_id = data.group_id
		data_method = self.method_info(self._NAME)
		method = data_method["methods"][1]
		url = f"{data_method['url']}{method}"	
		param = {
		"access_token": self.tokens[0],
		"v": self.v,
		"group_id": group_id,
		"sort": "id_asc",
		"count": 1000,
		"offset": 0
		}
		start = time.perf_counter() 
		response =  requests.post(url, params=param, headers=self.headers)
		end = time.perf_counter() 
		print(end-start)
		urls, items = [], []
		if response and not "error" in response.json():
			users_count = response.json().get("response", {}).get("count", 0)
			items.append(response.json()["response"]["items"])
			for step in range(1000, response.json().get("response", {}).get("count", 0)+1, 1000):
				shuffle(self.tokens)
				param.update({"offset": step, "access_token": self.tokens[0]})
				new_url = url + "?" + "".join([f"&{key}={value}" for key, value in param.items()])
				urls.append(new_url.replace("?&", "?"))
			response = grequests.map([grequests.AsyncRequest("POST", url, headers=self.headers) for url in urls])
			for data in response:
				if data and not "error" in data.json():
					items.append(data.json().get("response", {}).get("items"))
			return {"items": items, "count": users_count}
		elif not response:
			self._LOGGER.warning(f"{response.url} status code {response.status_code}.")
		return None		

class Friends(BaseClass):
	_NAME = "FRIENDS"
	
	def get_friends(self, data:DataFriends):
		if not isinstance(data, DataFriends):
			raise TypeError("data type is DataFriends")
		shuffle(self.tokens)
		user_id = data.user_id
		user_ids = data.user_ids
		data_friends = data.data_friends
		data_method = self.method_info(self._NAME)
		method = data_method["methods"][0]
		url = f"{data_method['url']}{method}"
		param = {
		"access_token": self.tokens[0],
		"v": self.v
		}
		if not user_ids is None:
			if user_id is None: user_ids.append(user_id)
			data = self._valid_data(user_ids, param, self._NAME, method, name_attr="user_ids")
			if isinstance(data, grequests.AsyncRequest):
				result =  grequests.map(data)
				users_data = []
				for data in result:
					if data and not "error" in data.json():
						users_data.append(data.json()["response"])
				return users_data
			response = requests.post(data[0], data=data[1], headers=self.headers)
			if response and not "error" in response.json():
				return response.json()["response"]
		param.update({"user_id": user_id})
		response = requests.get(url, params=param, headers=self.headers)
		if response and not "error" in response.json():
			count_friends = response.json()["response"]["count"]
			if data_friends and count_friends > 1:
				response = Profile(VKApi(self.tokens, self.v, self.headers, self.proxies)).get_profile(DataProfile(user_ids=response.json()["response"]["items"]))
				return {"items": response, "count": count_friends}
			elif data_friends and count_friends == 1:
				response = Profile(VKApi(self.tokens, self.v, self.headers, self.proxies)).get_profile(DataProfile(user_id=response.json()["response"]["items"][0]))
				return  {"items": response, "count": count_friends}
			return response.json()["response"]
		elif not response:
					self._LOGGER.warning(f"{response.url} status code {response.status_code}.")	

class Walls(BaseClass):
	_NAME = "WALLS"
	
	
	def get_wall(self, data: DataWalls):
		if not isinstance(data, DataWalls):
			raise TypeError("type data is DataWalls")
		shuffle(self.tokens)
		owner_id = data.owner_id
		owner_ids = data.owner_ids
		data_method = self.method_info(self._NAME)
		method = data_method["methods"][0]
		url = f"{data_method['url']}{method}"
		params = {
		"access_token": self.tokens[0],
		"v": self.v,
		"photo_sizes": 0,
		"count": 100,
		"offset": 0
		}
		if not owner_ids is None:
			if owner_id is None: owner_ids.append(owner_id)	
		params.update({"owner_id": owner_id})		
		response = requests.get(url, params=params, headers=self.headers)
		items = []
		if response and not "error" in response.json():
			wall_count = response.json()["response"]["count"]
			items.append(_CORRECTION_MODEL._correction_wall(response.json()["response"]))
			if wall_count > 100:
				new_wall = []
				for offset in range(100, wall_count+1, 100):
					shuffle(self.tokens)
					params.update({"offset": offset, "access_token": self.tokens[0]})
					new_wall.append(params.copy())
				response = [grequests.get(url, params=params) for params in new_params]
				result = grequests.map(response)
				for data in result:
					if data and not "error" in data.json():
						items.append(_CORRECTION_MODEL._correction_wall(response.json()["response"]))
					elif not data:
						self._LOGGER.warning(f"{data.url} status code {data.status_code}.")
			return items
		elif not response:
			self._LOGGER.warning(f"{response.url} status code {response.status_code}.")
		return None
