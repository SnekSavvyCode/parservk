from typing import Optional

from pydantic import BaseModel

VERSION_API = 5.132

class ParserVK(BaseModel):
	tokens: list[str]
	headers: dict[str, str]
	v_api: float = VERSION_API
	proxies: Optional[dict[str, str]] = None

class DataUsers(BaseModel):
	user_id: Optional[str] = None
	user_ids: Optional[list[str]] = None
	subscriptions: bool = False
	data_subscriptions: bool = False
	friends: bool = False
	data_friends: bool = False
	followers: bool = False
	data_followers: bool = False
	walls: bool = False

class DataGroups(BaseModel):
	group_id: Optional[str] = None
	group_ids: Optional[list[str]] = None
	ismember: bool = False
	user_id: Optional[str] = None
	user_ids: Optional[list[str]] = None

class DataFriends(BaseModel):
	user_id: Optional[str] = None
	user_ids: Optional[list[str]] = None
	data_friends: bool = False
	isgroup_id: bool = False

class DataWalls(BaseModel):
	owner_id: Optional[str] = None
	owner_ids: Optional[list[str]] = None