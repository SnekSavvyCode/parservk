from dataclasses import dataclass

VERSION_API = 5.132

@dataclass
class VKApi:
	tokens: list[str]
	v_api: float = VERSION_API
	headers: dict[str, str] = None
	proxies: dict[str, str] = None

@dataclass
class DataProfile:
	user_id: str = None
	user_ids: list[str] = None
	subscriptions: bool = False
	data_subscriptions: bool = False
	friends: bool = False
	data_friends: bool = False
	followers: bool = False
	data_followers: bool = False
	wall: bool = False

@dataclass
class DataGroups:
	group_id: str = None
	group_ids: list[str] = None
	ismember: bool = False
	user_id: str = None
	user_ids: list[str] = None


@dataclass
class DataFriends:
	user_id: str = None
	user_ids: list[str] = None
	data_friends: bool = False
	isgroup_id: bool = False

@dataclass
class DataWalls:
	owner_id: str = None
	owner_ids: list[str] = None
