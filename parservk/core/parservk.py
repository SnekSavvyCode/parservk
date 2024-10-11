from typing import Any, Optional, Union

from pydantic import BaseModel

from .base import Base
from .constants import VERSION_API, HEADERS
from .models import DataUsers, DataGroups, DataFriends, DataWall

from time import perf_counter as p
class Users(Base):
    """
    Wrapper over the users submethods.
    
    ** The full documentation can be viewed on the official website at the url: `https://dev.vk.com/en/method/users` **
    """
    
    fields_list = ['bdate', 'about', 'status', 'sex', 'domain', 'activities', 'books', 'city', 'country', 'contacts', 'photo_id', 'photo_max', 'nickname', 'schools', 'site', 'photo_50', 'photo_200', 'photo_100', 'photo_200_orig', 'photo_400_orig', 'verified', 'online', 'last_seen', 'quotes', 'relation', 'followers_count', 'career', 'counters', 'education', 'games', 'has_photo', 'home_town', 'interests', 'occupation', 'personal', 'screen_name', 'trending', 'tv', 'universities']

    _NAME = "USERS"
    _limits = {"user_ids": 1000}
    
    # Temporary implementation
    DATACLASS = DataUsers

    def get(self, ispool: bool = False, **kwargs: Any) -> Union[dict[str, list], list]:
        """
        Get user data based on provided params.
        
        ** The full documentation can be viewed on the official website at the url: `https://dev.vk.com/en/method/users.get` **

        :param ispool: Flag to indicate if using pool(This may be necessary when calling other submethods).
        :param kwargs: The main params of the query.
            :param user_id: Id user or username(Optional).
            :param user_ids: List users ids or usernames.
            :param friends: Flag about getting the user's friends if the number of users is equal to 1(Unofficial param).
            :param subscriptions: Flag about getting the user's subscriptions the number of users is equal to 1(Unofficial param).
            :param followers: Flag about getting the user's followers if the number of users is equal to 1(Unofficial param).
            :param wall: Flag about getting the user's walls if the number of users is equal to 1(Unofficial param).
            :param data_friends: Flag indicating whether to retrieve information about each friend, only if the friends param is set to True and and the number of users is equal to 1(Unofficial param).
            :param data_subscriptions: Flag indicating whether to retrieve information about each subscription, only if the subscriptions param is set to True and and the number of users is equal to 1(Unofficial param).
            :param data_followers: Flag indicating whether to retrieve information about each follower, only if the followers param is set to True and and the number of users is equal to 1(Unofficial param).
        :return: Dict containing user data if the ispool param is set to False, otherwise a list of querys.
            - "users": List of users. If no users have been specified, it returns an empty list.
            - "friends": List of friends. If no user have been specified, it returns an empty list or the friends param is set to False.
            - "subscriptions": List of subscriptions. If no user have been specified, it returns an empty list or the subscriptions param is set to False.
            - "followers": List of followers. If no user have been specified, it returns an empty list or the followers param is set to False.
            - "wall": List of walls. If no user have been specified, it returns an empty list or the wall param is set to False.
        """
        
        # Temporary implementation
        data = self.DATACLASS(**kwargs)
        user_id = data.user_id
        user_ids = data.user_ids
        querys = []
        params = self._update_all(params=self.base_params.copy(), fields=self.FIELDS)
        
        if not user_id is None:
            user_ids.append(user_id)
        querys.extend(
            self.get_querys_from_data(
                user_ids, params, submethod="get", multi_ids="user_ids"
            )
        )

        if ispool:
            return querys
        
        if data.subscriptions:
            querys.extend(self.getSubscriptions(user_id=user_id, ispool=True))

        if data.followers:
            querys.extend(self.getFollowers(user_id=user_id, ispool=True))

        if data.friends:
            querys.extend(self.parser.friends.get(user_id=user_id, ispool=True))

        if data.wall:
        	querys.extend(self.parser.wall.get(owner_id=user_id, ispool=True))
        self.poolmanager.add(querys)
        self.poolmanager.start(
            callable_func=self.handlers.main_handler,
            data_subscriptions=data.data_subscriptions,
            data_followers=data.data_followers,
            data_friends=data.data_friends,
        )
        
        
        result = self.poolmanager.callable_results[-1]
        users = result.get("users", {})
        friends = result.get("friends", {})
        wall = result.get("wall", {})
        return {"users": users.get("get", []), "friends": friends.get("get", []), "subscriptions": users.get("getsubscriptions", []), "followers": users.get("getfollowers", []), "wall": wall.get("get", [])}

    def getSubscriptions(self, ispool: bool = False, **kwargs: Any) -> list[dict[str, list]]:
        """
        Get user subscriptions based on provided params.
        
        ** The full documentation can be viewed on the official website at the url: `https://dev.vk.com/en/method/users.getSubscriptions` **
        
        :param ispool: Flag to indicate if using pool(This may be necessary when calling other submethods).
        :param kwargs: The main params of the query.
            :param user_id: Id user or username(Optional).
            :param data_subscriptions: Flag indicating whether to retrieve information about each subscription, only if the subscriptions param is set to True and and the number of users is equal to 1(Unofficial param).
        :return: A list of user subscriptions if the ispool param is set to False, otherwise a list of querys.
        """

        return self._get_connections(method="getsubscriptions", ispool=ispool,  **kwargs)

    def getFollowers(self, ispool: bool = False, **kwargs: Any) -> list[dict[str, list]]:
        """
        Get user followers based on provided params.
        
        ** The full documentation can be viewed on the official website at the url: `https://dev.vk.com/en/method/users.getFollowers` **
        
        :param ispool: Flag to indicate if using pool(This may be necessary when calling other submethods).
        :param kwargs: The main params of the query.
            :param user_id: Id user or username(Optional).
            :param data_followers: Flag indicating whether to retrieve information about each follower, only if the followers param is set to True and and the number of users is equal to 1(Unofficial param).
        :return: A list of user followers if the ispool param is set to False, otherwise a list of querys.
        """

        return self._get_connections(method="getfollowers", ispool=ispool,  **kwargs)

    def _get_connections(
        self, method: str = "getsubscriptions", ispool: bool = False, **kwargs: Any
    ) -> list[dict[str, list]]:
        """
        Wrapper over the getSubscriptions and getFollowers methods.
        
        ** We recommend using getSubscriptions and getFollowers instead of this method. **
        
        :param method: Name method(getsubscriptions, getfollowers).
        :param ispool: Flag to indicate if using pool(This may be necessary when calling other submethods).
        :param kwargs: The main params of the query.
            :param user_id: Id user or username(Optional).
            :param data_subscriptions: Flag indicating whether to retrieve information about each subscription, only if the subscriptions param is set to True and and the number of users is equal to 1(Unofficial param).
            :param data_followers: Flag indicating whether to retrieve information about each follower, only if the followers param is set to True and and the number of users is equal to 1(Unofficial param).
        :return: A list of user subscriptions or followers if the ispool param is set to False, otherwise a list of querys.
        """
        
        # Temporary implementation
        data = self.DATACLASS(**kwargs)
        method = method.lower()
        user_id = data.user_id
        if user_id is None:
            return []
        query = self.get_querys_from_data(
            [user_id], self._update_all(params=self.base_params.copy()), submethod = method, multi_ids="user_ids"
        )
        if ispool:
            return query
        self.poolmanager.add(query)
        self.poolmanager.start(
            callable_func=self.handlers.main_handler,
            data_subscriptions=data.data_subscriptions,
            data_followers=data.data_followers,
            
        )

        return self.poolmanager.callable_results[-1]["users"][method]

class Groups(Base):
    """
    Wrapper over the groups submethods.
    
    ** The full documentation can be viewed on the official website at the url: `https://dev.vk.com/en/method/groups` **
    """

    fields_list = ['id', 'name', 'screen_name', 'is_closed', 'deactivated', 'type', 'photo_50', 'photo_100', 'photo_200', 'activity', 'addresses', 'age_limits', 'city', 'contacts', 'counters', 'country', 'cover', 'crop_photo', 'description', 'has_photo', 'links', 'main_album_id', 'main_section', 'market', 'members_count', 'place', 'public_date_label', 'site', 'start_date', 'finish_date', 'status', 'trending', 'verified', 'wall', 'wiki_page']
    
    _NAME = "GROUPS"
    _limits = {"group_ids": 500, "user_ids": 500}
    
    # Temporary implementation
    DATACLASS = DataGroups

    def getById(self, ispool: bool = False, **kwargs: Any) -> list[dict]:
        """
        Get group data based on provided params.
        
        ** The full documentation can be viewed on the official website at the url: `https://dev.vk.com/en/method/groups.getById` **

        :param ispool: Flag to indicate if using pool(This may be necessary when calling other submethods).
        :param kwargs: The main params of the query.
            :param group_id: Id group or username(Optional).
            :param group_ids: List groups ids or usernames.
        :return: A list groups data if the ispool param is set to False, otherwise a list of querys.
        """

        # Temporary implementation
        data = self.DATACLASS(**kwargs)

        group_id = data.group_id
        group_ids = data.group_ids
        if not group_id is None:
            group_ids.append(group_id)
        params = self._update_all(params=self.base_params.copy(), fields=self.FIELDS)
        query = self.get_querys_from_data(
            group_ids, params, submethod="getbyid", multi_ids="group_ids"
        )
        if ispool:
            return query
        self.poolmanager.add(query)
        self.poolmanager.start(
            callable_func=self.handlers.main_handler,
          
        )
        return self.poolmanager.callable_results[-1]["groups"]["getbyid"]

    def isMember(self, ispool: bool = False, **kwargs: Any) -> list[Union[int, dict]]:
        """
        Check if a user is a member of a group.
        
        ** The full documentation can be viewed on the official website at the url: `https://dev.vk.com/en/method/groups.isMember` **
        
        :param ispool: Flag to indicate if using pool(This may be necessary when calling other submethods).
        :param kwargs: The main params of the query.
            :param group_id: Id group or username(Optional).
            :param user_id: Id user or username(Optional).
            :param user_ids: List users ids or usernames.
        :return: A list containing information about whether the user is a member of the group if the ispool param is set to False, otherwise a list of querys.
        """

        # Temporary implementation
        data = self.DATACLASS(**kwargs)

        group_id = data.group_id
        user_id = data.user_id
        user_ids = data.user_ids
        if not user_id is None:
            user_ids.append(user_id)
        params = self._update_all(params=self.base_params.copy(), group_id=group_id)
        query = self.get_querys_from_data(
            user_ids, params, submethod= "ismember", multi_ids="user_ids"
        )
        if ispool:
            return query
        self.poolmanager.add(query)
        self.poolmanager.start(callable_func=self.handlers.main_handler)
        return self.poolmanager.callable_results[-1]["groups"]["ismember"]

    def getMembers(self, ispool: bool = False, **kwargs: Any) -> list:
        """
        Retrieve members of a group based on provided params.

        ** The full documentation can be viewed on the official website at the url: `https://dev.vk.com/en/method/groups.getMembers` **

        :param ispool: Flag to indicate if using pool(This may be necessary when calling other submethods).
        :param kwargs: The main params of the query.
            :param group_id: Id group or username.
            :param count: Number of members to retrieve in one query. Default: 1000.
            :param offset: Offset needed to return a specific subset of members. Default: 0.
            :param sort: Sort order. Default: "id_asc"
            :param max: Maximum number of members to retrieve. Default: "all".
        :return: The list is divided into lists in each of them "count" ids if the ispool param is set to False, otherwise a list of querys.
        """

        # Temporary implementation
        data = self.DATACLASS(**kwargs)

        group_id = data.group_id
        count = data.count
        offset = data.offset
        params = self._update_all(
            params=self.base_params.copy(), count=count, offset=offset, sort=data.sort
        )
        multi_ids = "group_ids"
        query = self.get_querys_from_data(
            [group_id], params, submethod="getmembers", multi_ids=multi_ids
        )
        if ispool:
            return query
        self.poolmanager.add(query)
        self.poolmanager.start(
            callable_func=self.handlers.main_handler,
            params=params,
            count=count,
            min=offset + count,
            max=data.max,
            group_id=group_id,
            multi_ids=multi_ids
        )
        return self.poolmanager.callable_results[-1]["groups"]["getmembers"]


class Friends(Base):
    """
    Wrapper over the friends submethods.
    
    ** The full documentation can be viewed on the official website at the url: `https://dev.vk.com/en/method/friends` **
    """

    _NAME = "FRIENDS"
    _limits = {"user_ids": 1}
      
    # Temporary implementation
    DATACLASS = DataFriends

    def get(self, ispool: bool = False, **kwargs: Any) -> list[Union[dict, int]]:
        """
        Get friends data based on provided params.

        ** The full documentation can be viewed on the official website at the url: `https://dev.vk.com/en/method/friends.get` **

        :param ispool: Flag to indicate if using pool (This may be necessary when calling other submethods).
        :param kwargs: The main params of the query.
            :param user_id: Id user or username(Optional).
            :param user_ids: List of user ids or usernames.
            :param data_friends: Flag indicating whether to retrieve information about each friend(Unofficial param).
        :return: A list of friends data if the ispool param is set to False, otherwise a list of queries.
        """

        # Temporary implementation
        data = self.DATACLASS(**kwargs)

        user_id = data.user_id
        user_ids = data.user_ids
        if not user_id is None:
            user_ids.append(user_id)
        query = self.get_querys_from_data(
            user_ids, self._update_all(params=self.base_params.copy()), submethod="get", multi_ids="user_ids"
        )
        if ispool:
            return query
        self.poolmanager.add(query)
        self.poolmanager.start(
            callable_func=self.handlers.main_handler,
            data_friends=data.data_friends,
        )
        return self.poolmanager.callable_results[-1]["friends"]["get"]

class Wall(Base):
    """
    Wrapper over the wall submethods.
    
    ** The full documentation can be viewed on the official website at the url: `https://dev.vk.com/en/method/wall` **
    """

    _NAME = "WALL"
    _limits = {"user_ids": 1, "owner_ids": 1}
    
    # Temporary implementation
    DATACLASS = DataWall
    
    def get(self, ispool: bool = False, **kwargs: Any):
        """
        Retrieve wall posts based on provided params.

        ** The full documentation can be viewed on the official website at the url: `https://dev.vk.com/en/method/wall.get` **

        :param ispool: Flag to indicate if using pool(This may be necessary when calling other submethods).
        :param kwargs: The main params of the query.
            :param owner_id: Id of the owner of the wall(User or community).
            :param count: Number of posts to retrieve in one query. Default: 100.
            :param offset: Offset needed to return a specific subset of posts. Default: 0.
            :param max: Maximum number of posts to retrieve. Default: "all".
        :return: A list of wall posts if the ispool param is set to False, otherwise a list of queries.
        """

        # Temporary implementation
        data = self.DATACLASS(**kwargs)

        owner_id = data.owner_id
        count = data.count
        offset = data.offset
        params = self._update_all(params=self.base_params.copy(), count=count, offset=offset)
        query = self.get_querys_from_data(
            [owner_id], params, submethod="get", multi_ids="owner_ids"
        )
        if ispool:
        	return query
        self.poolmanager.add(query)
        self.poolmanager.start(
            callable_func=self.handlers.main_handler,
            count=count,
            owner_id=owner_id,
            max=data.max,
            min=count+offset,
            multi_ids="owner_ids",
            params=params
        )
        return self.poolmanager.callable_results[-1]["wall"]["get"]

class ParserVK(BaseModel):
    """
    The main class of the `parservk` lib, providing a interface to interact with the VK API(Has unofficial params and funcs).
    
    ** Not all methods and submethods are supported at the moment. You can help us and create your own concept of methods or submethods, then send it to the mail: `codecobra03@gmail.com` **

    :param tokens: Tokens to VK API.
    :param v_api: Version API. Default 5.132.
    :param headers: Headers.
    :param proxies: Proxies(Optional).
    :param _dynamic_methods: Private param for create methods.
    """

    tokens: set[str]
    v_api: float = VERSION_API
    headers: dict[str, Any] = HEADERS
    proxies: Optional[dict[str, Any]] = None

    _dynamic_methods: dict[str, Any] = {}
    
    def __init__(self, **kwargs: Union[set[str], float, dict[str, Any]]) -> None:
    	super().__init__(**kwargs)
    	self.__create_dynamic_methods()
    
    # Temporary implementation
    def __call__(self, method: str, submethod: str, **kwargs: Any):
    	"""
    	One of the options for accessing the method's submethod and getting data by kwargs.
    	"""

    	class_ = getattr(self, method.lower())
    	
    	try:

    		return getattr(class_, submethod)(**kwargs)
    	
    	except Exception as e:

    		return None

    def __getattr__(self, name: str) -> Any:
        """
        Get a dynamic methods.
        
        :return: Value by attr name.
        """
        
        return self._dynamic_methods.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set a dynamic methods.
        """
        
        self._dynamic_methods[name] = value
    
    def __create_dynamic_methods(self) -> None:
    	"""
    	Creates the main sections(methods) for working with the VK API.
    	
    	** All available sections(methods) and their submethods can be viewed on the official website at the url: `https://dev.vk.com/en/method` **
    	"""
    	
    	for subclass in Base.__subclasses__():
    		self._dynamic_methods[subclass.__name__.lower()] = subclass(self)