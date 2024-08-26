import grequests
import requests

from typing import Union

class PoolManager:
    """
    A class for managing a pool of tasks.
    """
    
    __supported_types = ["grequests", "requests"]
    _results = []
    _tasks = []
    _tasks_type = None
    
    @classmethod
    def is_supported(cls, tasks: list[Union[str, dict, grequests.AsyncRequest]]) -> tuple[Union[bool, str, None]]:
        """
        Check if this task is supported and it is the same for all tasks.

        :param task: The task to check.
        :return: A tuple containing a boolean indicating whether the tasks are supported, and a string indicating the type of tasks if supported or None otherwise.
        """
        
        if all(isinstance(task, grequests.AsyncRequest) for task in tasks):
        	if all(isinstance(task, grequests.AsyncRequest) for task in cls._tasks):
        		return (True, cls.__supported_types[0])
        elif all(isinstance(task, (str, dict)) for task in tasks):
        	if all(isinstance(task, (str, dict)) for task in cls._tasks):
        		return (True, cls.__supported_types[1])
        return (False, None)
        		
    def add(self, tasks):
        """
        Add tasks to the pool.

        :param tasks: A list of tasks or a single task to add.
        :raises TypeError: If the type of tasks is not supported.
        """
        
        if not isinstance(tasks, list): tasks = [tasks]
        check_supported = self.is_supported(tasks)
        if check_supported[0]:
        	if not self._tasks_type: self._tasks_type = check_supported[1]
        	self._tasks.extend(tasks)
        else:
        	TypeError("The type must be the same for all tasks and belong to (str, grequests.AsyncRequest, dict)")

    def _clear_results(self) -> None:
    	"""
        Clear the results list.
        """
        
    	self._results.clear()
    
    def clear(self) -> None:
    	"""
        Clear the tasks list and reset the tasks type
        """
        
    	self._tasks_type = None
    	self._tasks.clear()
    
    def clear_all(self) -> None:
    	"""
        Clear both the tasks and results lists.
        """
        
    	self.clear()
    	self._clear_results()
    	
    def start(self, callable_func: callable = None) -> None:
    	"""
        Start processing the tasks.

        :param callable_func: A function to call with the results. Defaults to None.
        """
        
    	self._clear_results()
    	result = self._process_tasks()
    	if callable_func: callable_func(result)
    	self.clear()
   

    def _process_tasks(self) -> list:
        """
        Process the tasks based on their type.

        :return: A list of results from the tasks.
        """
        
        if self._tasks_type == "grequests":
        	response = self._process_grequests()
        elif self._tasks_type == "requests":
        	response = self._process_requests()
        else:
        	response = None
        return response
        
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
        
    	for task in tasks:
    		if isinstance(task, str):
    			response = requests.post(task)
    		else:
    			response = requests.post(**task)
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
    def tasks(self, new_tasks: list[Union[str, dict, grequests.AsyncRequest]]) -> list[Union[str, dict, grequests.AsyncRequest]]:
    	"""
        Set the tasks list.

        :param new_tasks: A list of tasks to set.
        :raises TypeError: If the new tasks list is not a list.
        :return: The updated tasks list.
        """

    	if not isinstance(new_tasks, list):
    		raise TypeError(f"Tasks should be of the list type, not the type {new_tasks.__class__.__name__}")
    	
    	self._tasks = new_tasks
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
    	if not new_type in self.__supported_types:
    		raise TypeError(f"The type is not supported, select from the list {self.__supported_types}")
    		
    	self._tasks_type = type
    	return self._tasks_type
    
    @property
    def results(self) -> list:
    	"""
    	Get the results.
    	
    	:return: The result of the tasks.
    	"""
    	
    	return self._results