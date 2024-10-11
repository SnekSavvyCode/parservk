import grequests
from typing import Any, Union, Optional
from random import shuffle

from .initmixin import InitMixin
from .utils import called_from

class Base(InitMixin):
    """
    The Base class is a base class for working with the VK API.
    It provides methods for creating requests, paginating queries, and updating access tokens and other methods.
    """
    
    _NAME = "BASE"
    URL_API = "https://api.vk.com/method/"

    BASE_DICT = {
        "url": str,
        "methods": dict[str, str],
        "multi_ids": list[str],
        "name": str,
    }
    
    def _create_requests(
        self,
        url: str,
        *,
        params: dict[str, Any] = {},
        headers: dict[str, Any] = {},
        proxies: dict[str, Any] = {},
        data: dict[str, Any] = {},
        type_query: str = "post",
    ) -> dict[str, Any]:
        """
        Creates a request.

        :param url: The URL of the server to which the request will be sent.
        :param params: The request parameters.
        :param headers: The request headers.
        :param proxies: The proxy servers for the request.
        :param data: The request data.
        :param type_query: The type of request (post or get). Default: post.
        :return: A dictionary with the request parameters.
        """

        if type_query == "post":
            if not len(data):
                data = self.update_params(params=params, **headers, **proxies)
            query = {"url": url, "data": data}

        elif type_query == "get":
            query = {
                "url": url,
                "params": params,
                "headers": headers,
                "proxies": proxies,
            }

        return query

    def _create_grequests(
        self,
        url: str,
        *,
        params: dict[str, Any] = {},
        headers: dict[str, Any] = {},
        proxies: dict[str, Any] = {},
        data: dict[str, Any] = {},
        type_query: str = "post",
    ) -> grequests.AsyncRequest:
        """
        Creates an asynchronous request.

        :param url: The URL of the server to which the request will be sent.
        :param params: The request parameters.
        :param headers: The request headers.
        :param proxies: The proxy servers for the request.
        :param data: The request data.
        :param type_query: The type of request (post or get). Default: post.
        :return: A grequests.AsyncRequest object with the request parameters.
        """

        if type_query == "post":
            if not len(data):
                data = self.update_params(params=params, **headers, **proxies)
            return grequests.post(url, data=data, session=self.poolmanager.session)

        elif type_query == "get":
            return grequests.get(url, params=params, headers=headers, proxies=proxies, session=self.poolmanager.session)

    def _create_query(
        self,
        url: str,
        *,
        params: dict[str, Any] = {},
        headers: dict[str, Any] = {},
        proxies: dict[str, Any] = {},
        data: dict[str, Any] = {},
        type_query: str = "post",
        type_lib: str = "grequests",
    ) -> Union[None, dict, grequests.AsyncRequest]:
        """
        Creates a query to the server at the specified URL with the given parameters, headers, and data using the specified library.

        :param url: The URL of the server to which the query will be sent.
        :param params: The query parameters.
        :param headers: The query headers.
        :param proxies: The proxy servers for the query.
        :param data: The query data.
        :param type_query: The type of query (post or get). Default: post.
        :param type_lib: The library to use for the query (grequests or requests). Default: grequests.
        :return: A dictionary with the query parameters if using "requests", or a grequests.AsyncRequest object if using "grequests".
        """

        if type_lib == "grequests":
            return self._create_grequests(
                url,
                params=params,
                headers=headers,
                proxies=proxies,
                data=data,
                type_query=type_query,
            )
        elif type_lib == "requests":
            return self._create_requests(
                url,
                params=params,
                headers=headers,
                proxies=proxies,
                data=data,
                type_query=type_query,
            )

    def _paginate_querys(
        self,
        ids: Union[str, int, list[str, int]],
        method: str,
        submethod: str,
        params: dict[str, Any],
        min: int,
        max: int,
        count: int,
        **kwargs: Any,
    ) -> list:
        """
        Creates a list of queries for paginated data retrieval.

        :param ids: A list of identifiers for the query.
        :param method: The method for retrieving data.
        :param submethod: The submethod for retrieving data.
        :param params: The query parameters.
        :param min: The minimum value for paginated query.
        :param max: The maximum value for paginated query.
        :param count: The number of elements per page.
        :param kwargs: Additional parameters for the query.
        :return: A list of queries for paginated data retrieval.
        """

        querys = []

        if not isinstance(ids, list):
            
            ids = [ids]

        for offset in range(min, max, count):

            url = self.get_data_from_method(method, submethod)[-1]
            params = params.copy()
            self._update_all(params=params, offset=offset)
            querys.extend(self.get_querys_from_data(ids, params, method, submethod, **kwargs))

        return querys

    def _update_access_token(self, params: dict) -> dict:
        """
        Updates the access token and returns the updated parameters.

        :param params: A dictionary of parameters.
        :return: The updated parameters with a new access token.
        """

        return self.update_params(params=params, access_token=list(self.tokens)[0])

    @staticmethod
    def update_params(params: dict, **kwargs: Any) -> dict:
        """
        Updates a dictionary of parameters.

        :param params: A dictionary of parameters.
        :param kwargs: Additional parameters to update.
        :return: The updated dictionary of parameters.
        """

        params.update(kwargs)

        return params

    def _update_all(self, params: dict, **kwargs: Any) -> dict:
        """
        Updates the access token and all parameters.

        :param params: A dictionary of parameters.
        :param kwargs: Additional parameters to update.
        :return: The updated parameters with a new access token.
        """

        self._update_access_token(params)
        
        return self.update_params(params=params, **kwargs)

    def __get_querys(self, ids: list[str, int], **kwargs: Any) -> list:
        """
        Creates a list of queries for a list of identifiers.

        :param ids: A list of identifiers.
        :param kwargs: Additional parameters for the query (multi_ids).
        :return: A list of querys.
        """

        querys = []
        params = kwargs.get("params", {})
        multi_ids = kwargs.get("multi_ids")
        url = kwargs.get("url")

        for partial_ids in ids:

            self._update_all(params=params, **self.headers, **{multi_ids: partial_ids})
            querys.append(self._create_query(url, data=params))

        return querys

    def __get_query(self, id: list[str, int], **kwargs: Any) -> list:
        """
        Creates a query for a single identifier.

        :param id: An identifier.
        :param kwargs: Additional parameters for the query.
        :return: A list with a single query.
        """

        params = kwargs.get("params", {})
        multi_ids = kwargs.get("multi_ids", "").replace("ids", "id")
        url = kwargs.get("url")
        self._update_all(params=params, **self.headers, **{multi_ids: id[0]})

        return [self._create_query(url, data=params)]

    def _get_querys_from_ids(
        self, data_ids: tuple[bool, list, int], **kwargs: Any
    ) -> list[dict, grequests.AsyncRequest]:
        """
        Returns a list of queries based on the provided identifiers.

        :param data_ids: a tuple containing three elements:
            :param bool: bool flag if the request is a multi-query.
            :param list: list of identifiers.
            :param int: length list ids.
        :param kwargs: Additional keyword arguments.
        :return: A list of queries as dictionaries or asynchronous requests.
        """

        if data_ids[0]:
            
            return self.__get_querys(ids=data_ids[1], **kwargs)
            
        elif data_ids[-1]:
            
            return self.__get_query(id=data_ids[1], **kwargs)
            
        return []

    @staticmethod
    def _format_ids(
        ids: list[str, int],
        max_ids_per_group: int,
        callable_func: callable = None,
        **kwargs: Any,
    ) -> tuple[bool, Union[str, list], int]:
        """
        Formats a list of ids based on the maximum number of ids per group.

        :param ids: A list of ids.
        :param max_ids_per_group: The maximum number of ids per group.
        :param callback_func: A function that will be called with the formatted data(Optional).
        :param kwargs: Additional arguments for callback_func.

        :return: A tuple containing a boolean value, a list or individual values depending on the number of elements in the ids list, and the total number of ids.
            - The boolean value indicates whether the maximum number of ids was exceeded.
            - If the number of ids exceeds max_ids_per_group, the function returns a list of strings, where ids are divided into groups of max_ids_per_group ids per group.
            - If the number of ids does not exceed max_ids_per_group, the function returns a list with a single string containing all ids.
            - If the number of ids is 0 or 1, the function returns a tuple with False and individual id values.
        """

        length = len(ids)
        
        if length > max_ids_per_group:
            
            formatted_ids = (
                True,
                [
                    ", ".join(map(str, ids[step : step + max_ids_per_group]))
                    for step in range(0, len(ids) + 1, max_ids_per_group)
                ],
                length,
            )
            
        elif 1 < length <= max_ids_per_group:
            
            formatted_ids = (True, [", ".join(map(str, ids))], length)
            
        else:
            
            formatted_ids = (False, ids, length)
            
        if callable_func:
            
            return callable_func(data_ids=formatted_ids, **kwargs)

        return formatted_ids

    def _data_from_method(self, method: str) -> dict:
        """
        Get information about the API VK section.

        :param method: Section API VK(Users, Groups, ...).
        :raises ValueError: If method not in methods.
        :return: Dict with information about the API VK section.
        """

        if not method in self._methods:
            
            raise ValueError("Method is not valid.")
            
        return self._methods[method]

    def get_querys_from_data(
        self,
        ids: list[str, int],
        params: dict,
        method: Optional[str] = None,
        submethod: Optional[str] = None,
        **kwargs: Any,
    ) -> list:
        """
        Generates a list of queries for data retrieval from the API based on input parameters.

        :param ids: Identifiers for which the requests will be sent.
        :param params: Parameters to be added to the query.
        :param method: Section API VK(Users, Groups, ...)(Optional).
        :param submethod: The name of the section's submethod(Optional).
        :param kwargs: Additional parameters for the query (multi_ids).
        :return: A list of querys.
        """
        
        
        method = method or self._NAME
        submethod = submethod or called_from(True)
        data_method = self.get_data_from_method(method.upper(), submethod)
        multi_ids = kwargs.get("multi_ids", data_method[0]["multi_ids"][0])
        limits_per_category = self._limits_per_category[method.upper()].get(multi_ids, 1)

        return self._format_ids(
            ids=ids,
            max_ids_per_group=limits_per_category,
            callable_func=self._get_querys_from_ids,
            url=data_method[-1],
            params=params.copy(),
            multi_ids=multi_ids,
        )

    def get_data_from_method(self, method: str, submethod: str) -> tuple[dict, str]:
        """
        Get data about method API VK.

        :param method: Section API VK(Users, Groups, ...).
        :param submethod: The name of the section's submethod.
        :return: tuple 0 index data dict and 1 index url to apply.
        """

        data_method = self._data_from_method(method.upper())

        return (
            data_method,
            data_method["url"] + data_method["methods"][submethod.lower()],
        )