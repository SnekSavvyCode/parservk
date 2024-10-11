import inspect

import grequests
import requests

from typing import Any, Union, Optional

class PoolManager:
    """
    A class for managing a pool of tasks.
    """
    
    __states_dict = {0: "empty", 1: "waiting", 2: "executing", 3: "completed"}
    __supported_types = ["grequests", "requests"]
    __supported_types_dict = {"grequests": grequests.AsyncRequest, "requests": (str, dict)}
    __passed_attrs_for_merge = ["_results", "_callable_results", "_processed_func"]
    session = requests.Session()

    def __init__(self):
        self._processed_func = {name.split("_")[-1]: func for name, func in inspect.getmembers(self, predicate=inspect.ismethod) if name.split("_")[-1] in self.__supported_types}
        self._results = []
        self._callable_results = []
        self._tasks = []
        self._tasks_ids = []
        self._tasks_type = None
        self.state = 0

    @staticmethod
    def get_id(request: Union[str, dict, grequests.AsyncRequest]) -> int:
        """
        Get id query.

        :param query: query.
        :return: id.
        """
        return id(request)
    
    def get_ids(
        self, querys: list[Union[str, dict, grequests.AsyncRequest]]
    ) -> list[int]:
        """
        Get ids querys and results.

        :param querys: querys.
        :return: list ids.
        """

        return [self.get_id(query) for query in querys]

    def get_first_id(self, default: Optional[Any] = None) -> Optional[Union[int, Any]]:
        """
        Get first id from tasks ids.
        :param default: The default value if the length of the task ids is 0(Optional).
        :return: first id if length of the task ids != 0 else default(Optional).
        """

        if not self.is_state_waiting():
            return default
        
        return self._tasks_ids[0]

    def get_last_id(self, default: Optional[Any] = None) -> Optional[int]:
        """
        Get last id from tasks ids.
        :param default: The default value if the length of the task ids is 0(Optional).
        :return: last id if length of the task ids != 0 else default(Optional).
        """

        if not self.is_state_waiting():
            return default
        
        return self._tasks_ids[-1]

    def get_central_id(self) -> list[int]:
        """
        Get central id.

        :return: list central ids if length % 2 != 0 else list central id.
        """

        length = len(self._tasks_ids)
        central_index = length // 2

        if length % 2 == 0:
            return self._tasks_ids[central_index - 1 : central_index + 1]
        return [self._tasks_ids[central_index]]
    
    def is_state_empty(self) -> bool:
        """
        Check if the state is empty (0).

        :return: True if the state is empty, False otherwise.
        """
        
        return self.state == 0

    def is_state_waiting(self) -> bool:
        """
        Check if the state is waiting (1).

        :return: True if the state is waiting, False otherwise.
        """
        
        return self.state == 1

    def is_state_executing(self) -> bool:
        """
        Check if the state is executing (2).

        :return: True if the state is executing, False otherwise.
        """
        
        return self.state == 2

    def is_state_completed(self) -> bool:
        """
        Check if the state is completed (3).

        :return: True if the state is completed, False otherwise.
        """

        return self.state == 3

    def is_same_type(self, tasks: list[Union[str, list, grequests.AsyncRequest]], check_to_type: Optional[object] = None) -> bool:
        """
        Check if all tasks are of the same type as check_to_type or self._tasks_type.

        :param tasks: List of tasks to check.
        :param check_to_type: Type to check against, defaults to self._tasks_type.
        :return: True if all tasks are of the same type, False otherwise.
        """

        check_to_type = check_to_type or self.__supported_types_dict.get(self._tasks_type)
        return all([isinstance(task, check_to_type) for task in tasks])

    def is_supported(
        self, tasks: list[Union[str, dict, grequests.AsyncRequest]]
    ) -> tuple[Union[bool, Union[str, None]]]:
        """
        Check if this task is supported and it is the same for all tasks.

        :param task: The task to check.
        :return: A tuple containing a boolean indicating whether the tasks are supported, and a string indicating the type of tasks if supported or None otherwise.
        """
        
        if self.is_state_empty() or self.is_state_completed():
        	for lib, obj in self.__supported_types_dict.items():
        		if self.is_same_type(tasks, obj):
        			
        			return (True, lib)

        	return (False, None)

        return (self.is_same_type(tasks), self._tasks_type)

    def add(self, tasks: list[str, grequests.AsyncRequest, dict]) -> list[int]:
        """
        Add tasks to the pool.

        :param tasks: A list of tasks or a single task to add.
        :return: list tasks ids.
        :raises TypeError: If the type of tasks is not supported.
        """

        if not isinstance(tasks, list):
            tasks = [tasks]
        check_supported = self.is_supported(tasks)
        if check_supported[0]:
            self._tasks_type = self._tasks_type or check_supported[1]
            ids = self.get_ids(tasks)
            self._tasks_ids.extend(ids)
            self._tasks.extend(tasks)
            self.state = 1
            return ids
        raise TypeError(
            "The type must be the same for all tasks and belong to (str, grequests.AsyncRequest, dict)"
        )

    def _clear_callable_results(self) -> None:
        """
        Clear the callable results.
        """

        self._callable_results.clear()

    def _clear_tasks_ids(self) -> None:
        """
        Clear the tasks ids list.
        """

        self._tasks_ids.clear()

    def _clear_results(self) -> None:
        """
        Clear the results list.
        """

        self._results.clear()
    
    def clear_results_all(self):
    	"""
    	Clear the results list and the callable results.
    	"""
    	
    	self._clear_results
    	self._clear_callable_results()

    def clear(self) -> None:
        """
        Clear the tasks list and reset the tasks type
        """

        self._tasks_type = None
        self._tasks.clear()

    def clear_all(self) -> None:
        """
        Clear both the tasks, tasks ids, results lists, callbale results list.
        """

        self.clear()
        self.clear_results_all()
        self._clear_tasks_ids()

    def start(self, callable_func: callable = None, **kwargs: Any) -> None:
        """
        Start processing the tasks.

        :param callable_func: A function to call with the results. Defaults to None.
        :param kwargs: Named arguments for callable func(Any names except results and ids).
        """
        
        if not self.is_state_waiting():
        	return
        if self.is_state_completed():
        	self.clear_results_all()
        self.state = 2
        results = self._process_tasks()
        results_ids = self._tasks_ids
        self.clear()

        if callable_func:
            self._callable_results.append(
                callable_func(results=results, ids=self._tasks_ids, **kwargs)
            )
        self._clear_tasks_ids()
        self.state = 3
    
    def _get_attrs_from_init(self) -> list[str]:
        """
        Retrieves a list of attributes defined in the object's __init__ method.

        :return: List of attributes defined during object initialization.
        """

        return list(set(self.__dict__) - set(self.__init__.__code__.co_varnames))
    	
    def merge(self, other: object) -> object:
    	"""
    	Merge class instances by task and task ID.
    	
    	:param other: An instance of the PoolManager class.
    	:raises: TypeError If the task type is different.
    	:return: New instance PoolManager.
    	"""

    	if self._compare_type_tasks(other):
    		pool = PoolManager()
    		for attr in self._get_attrs_from_init():
    			self_attr = getattr(self, attr)
    			other_attr = getattr(other, attr)
    			if isinstance(self_attr, list):
    				if not attr in self.__passed_attrs_for_merge:
    					setattr(pool, attr, self_attr + other_attr)
    				continue
    			
    			if attr == "state":
    				setattr(pool, attr, max(self_attr, other_attr) if max(self_attr, other_attr) < 2 else 1)
    				continue
    			
    			setattr(pool, attr, self_attr or other_attr)
    			
    		return pool
    	
    	raise TypeError("The type of the other and this instance must be the same.")

    def _compare_type_tasks(self, other: object) -> bool:
    	"""
    	Checking for equality of task types.
    	
    	:param other: An instance of the PoolManager class.
    	:return: True if the types are equal, otherwise False.
    	"""
    	
    	return self._tasks_type == other._tasks_type or self._tasks_type is None or other._tasks_type is None

    def _process_tasks(self) -> list:
        """
        Process the tasks based on their type.

        :return: A list of results from the tasks.
        """

        func = self._processed_func.get(self._tasks_type)

        return func() if func else None

    def _process_grequests(self) -> list:
        """
        Process the tasks using grequests.

        :return: A list of results from the tasks.
        """
        response = grequests.map(self._tasks)
        self._results.extend(response)
        return response

    def _process_requests(self) -> list:
        """
        Process the tasks using requests.

        :return: A list of results from the tasks.
        """
        
        for task in self._tasks:
            if isinstance(task, str):
                response = self.session.post(task)
            else:
                response = self.session.post(**task)
            self._results.append(response)

        return self._results

    @property
    def tasks(self) -> list[Union[str, dict, grequests.AsyncRequest]]:
        """
        Get the tasks list.

        :return: A list of tasks.
        """

        return self._tasks

    @tasks.setter
    def tasks(
        self, new_tasks: list[Union[str, dict, grequests.AsyncRequest]]
    ) -> list[Union[str, dict, grequests.AsyncRequest]]:
        """
        Set the tasks list.

        :param new_tasks: A list of tasks to set.
        :raises TypeError: If the new tasks list is not a list.
        :return: The updated tasks list.
        """

        if not isinstance(new_tasks, list):
            raise TypeError(
                f"Tasks should be of the list type, not the type {new_tasks.__class__.__name__}"
            )
        self._tasks = new_tasks
        self._tasks_ids = get_ids(self._tasks)
        return self._tasks

    @property
    def type(self) -> Union[str, None]:
        """
        Get the tasks type.

        :return: The type of tasks.
        """

        return self._tasks_type

    @type.setter
    def type(self, new_type: str) -> Union[str, None]:
        """
        Set the tasks type.
        
        :param new_type: New tasks type.
        :raises TypeError: If the new type is not among the supported types.
        :return: The updated tasks type.
        """

        if not new_type in self.__supported_types:
            raise TypeError(
                f"The type is not supported, select from the list {self.__supported_types}"
            )

        self._tasks_type = type
        return self._tasks_type

    @property
    def results(self) -> list:
        """
        Get the results.

        :return: The result of the tasks.
        """

        return self._results

    @property
    def callable_results(self) -> list:
        """
        Get the results from callable func.

        :return: The result of the execution callable func.
        """

        return self._callable_results

    @property
    def tasks_ids(self) -> list:
        """
        Get the tasks ids.

        :return: responses Indicators.
        """

        return self._tasks_ids