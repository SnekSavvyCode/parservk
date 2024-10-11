from __future__ import annotations

from typing import Any, TYPE_CHECKING

from .subquery import SubQuery
from .utils import create_compiles, get_submethods_from_method

from time import perf_counter as p
if TYPE_CHECKING:
    from ..poolmanager import PoolManager
    from ..parservk import ParserVK


class Handlers:
    """
    Class for handling requests to the VK API.
    """

    def __init__(self, poolmanager: PoolManager, parser: ParserVK) -> None:
        """
        Initializes the class.

        :param poolmanager: Class instance PoolManager.
        :param parser: Class instance ParserVK.
        """
        
        self._processed_ids = []
        self._processed_subquerys = []
        
        self.poolmanager = poolmanager
        self.parser = parser

        self._re_compiles = create_compiles(parser=self.parser, poolmanager=self.poolmanager, handlers=self)
        self.results = self.create_results()
    
    @staticmethod
    def create_submethods(method: str, skipped_handlers: list[str]) -> dict:
    	"""
    	Extracts submethods from the specified method.
    
        :param method: The name of the method.
        :param passed_handlers: Handlers to skip.
       :return: A dictionary of submethods.
    	"""

    	return get_submethods_from_method(method, skipped_handlers)

    def create_results(self) -> dict[str, dict[str, list]]:
        """
        Creates a dictionary for storing processing results.

        :return: Dictionary with processing results.
        """

        results = {}
        for _, classhandler, name in self._re_compiles:
            results[name] = {key: [] for key in classhandler._submethods_handler}


        return results

    def start_subquerys(self, **kwargs: Any) -> None:
        """
        Starts a subquerys.

        :param kwargs: Arguments for the subquery.
        """

        for subquery in self._processed_subquerys:
            kwargs.update(subquery.params)
        self.poolmanager.start(callable_func=self.main_handler, **kwargs)

    def update_subquery_data_handler(self, id: int, subquery_result: list) -> None:
        """
        Update subquery data handler.

        :param id: Subquery id.
        :param subquery_result: Subquery result.
        """

        for subquery in self._processed_subquerys:

            if id in subquery.ids:

                self._processed_ids.remove(id)

                subquery.update_results(id, subquery_result)

                return

    def push_subquery_results_handler(self) -> None:
        """
        Handlers pushing subquery results.
        """

        for subquery in self._processed_subquerys:
            if subquery.is_processed_ids_complete():

                subquery.push_results(self.results)

    def is_subquery(self, classhandler: object, callable_result: Any) -> bool:
        """
        Checks if the callable result is a subquery and processes it accordingly.

        ** If the callable result is an instance of SubQuery, this method extends the processed ids with the subquery ids
        from the class handler and appends the subquery to the list of processed subqueries. **

        :param classhandler: The class handler object.
        :param callable_result: The result of the callable, which can be of any type.
        :return: True if the callable result is a subquery, False otherwise.
        """

        if isinstance(callable_result, SubQuery):

            self._processed_ids.extend(classhandler._subquerys_ids)

            self._processed_subquerys.append(callable_result)

            return True

        return False
    
    def is_completed_subquery(self) -> bool:
    	"""
    	Check if the subquerys are completed.
    	:return: True if the subquerys are completed, False otherwise.
    	"""
    	
    	return not len(self._processed_ids) and len(self._processed_subquerys)

    def main_handler(
        self, results: list, ids: list[int], **kwargs: Any
    ) -> dict[str, dict[str, list]]:
        """
        Primary request handler.

        :param results: List of request results.
        :param ids: List of request ids.
        :param kwargs: Arguments for requests.
        :return: Dictionary with processing results.
        """

        for result, id in zip(results, ids):
            url = result.url

            for compile, classhandler, name in self._re_compiles:

                if compile.fullmatch(url):

                    callable_result = classhandler.main_handler(
                        result=result, id=id, **kwargs
                    )

                    if id in self._processed_ids:

                        self.update_subquery_data_handler(id, callable_result)

                    else:
           
                        result = self.results[classhandler.name][classhandler.method]

                        if not isinstance(callable_result, list):

                            result.append(callable_result)

                        else:

                            result.extend(callable_result)

                    self.is_subquery(classhandler, callable_result)

                    break

        if self.is_completed_subquery():
            self.push_subquery_results_handler()

        if self.poolmanager.is_state_waiting():

            self.start_subquerys(**kwargs)

            return self.poolmanager.callable_results[0]           
        
        return self.results