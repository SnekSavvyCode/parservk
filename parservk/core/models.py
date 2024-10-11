from typing import Optional, Union

from pydantic import BaseModel

class DataBase(BaseModel):
	user_id: Optional[Union[str, int]] = None
	user_ids: list[Union[str, int]] = []
	sort: str = "id_asc"
class DataGroupsAndWall(BaseModel):
	count: int = 1000
	offset: int = 0
	max: Union[int, str] = "all"
class DataUsers(DataBase):
	subscriptions: bool = False
	data_subscriptions: bool = False
	friends: bool = False
	data_friends: bool = False
	followers: bool = False
	data_followers: bool = False
	wall: bool = False

class DataGroups(DataBase, DataGroupsAndWall):
	group_id: Optional[Union[str, int]] = None
	group_ids: list[str, int] = []

class DataFriends(DataBase):
	data_friends: bool = False

class DataWall(DataGroupsAndWall):
	count: int = 100
	owner_id: Optional[Union[str, int]] = None
	owner_ids: list[Union[str, int]] = []