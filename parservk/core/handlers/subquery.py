from typing import Any, Union, Optional


class SubQuery:
    """
    Represents a subquery with a set of ids, a path, and parameters.
    """

    def __init__(
        self,
        ids: Union[list, tuple, set],
        path_subquery: str,
        params: dict = {},
        base_results: Optional[list[tuple[str, Any]]] = None,
        groups_by: list[dict[str, list]] = None,
    ):
        """
        Initializes the SubQuery instance.

        :param ids: A list, tuple, or set of ids for the subquery.
        :param path_subquery: The path of the subquery.
        :param params: A dictionary of parameters for the subquery. Default: {}.
        :param base_results: First results for subquery (optional).
        :param groups_by: List of dictionaries, where key is the name by which the value is grouped - list of ids for grouping (optional).
        """

        self.ids = set(ids)
        self.path_subquery = path_subquery
        self.params = params
        self.groups_by = groups_by if groups_by else []
        self._create_groups()
        self._processed_ids = self.ids.copy()

        if not base_results is None:
            for id, query_result in base_results:
                if not id in self.ids:
                    self.ids.add(id)
                    self._processed_ids.add(id)
                self.update_results(id, query_result)

        self._method_alias = self._get_handler_method_alias()
        self._submethod = self._get_handler_submethod()

    def _create_groups(self):
        """
        Create groups in results.
        """

        self.results = []
        for group_by in self.groups_by:
            group_dict = {}
            for name, _ in group_by.items():
                group_dict[name] = []
            self.results.append(group_dict)

        return self.results

    def _get_handler_method_alias(self):
        """
        Returns the method alias for the subquery.

        :return: The method alias as a string.
        """

        return self.path_subquery.split(".")[0]

    def _get_handler_submethod(self) -> str:
        """
        Returns the submethod for the subquery.

        :return: The submethod as a string.
        """

        return self.path_subquery.split(".")[-1]

    def _remove_processed_id(self, id: int) -> None:
        """
        Removes a processed id from the subquery.
        :param id: The id to remove.
        """

        self._processed_ids.discard(id)

    def _remove_processed_ids(self, ids: Union[list, tuple, set]) -> None:
        """
        Removes a set of processed ids from the subquery.

        :param ids: A list, tuple, or set of ids to remove.
        """

        self._processed_ids.difference_update(ids)

    def is_id_in_groups_by(self, id: int):
        """
        Checks if an id is in the groups.

        :param id: The id to check.
        :return: name group if the id is in the groups, False otherwise.
        """

        for group_by in self.groups_by:
            for name, ids in group_by.items():

                if id in ids:

                    return name

        return False

    def is_id_in_subquery(self, id: int):
        """
        Checks if an id is in the subquery.

        :param id: The id to check.
        :return: True if the id is in the subquery, False otherwise.
        """

        return id in self.ids

    def is_ids_in_subquery(self, ids: Union[list, tuple, set]) -> bool:
        """
        Checks if a set of ids is in the subquery.

        :param ids: A list, tuple, or set of ids to check.
        :return: True if all ids are in the subquery, False otherwise.
        """

        return self.ids.issubset(set(ids))

    def is_processed_ids_complete(self) -> bool:
        """
        Checks if all ids are processed.

        :return: True, if all the ids processed otherwise are False.
        """

        return not len(self._processed_ids)

    def is_other_method(self, other_method: str) -> bool:
        """
        Checks if the subquery's method alias is different from another method.

        :param other_method: The other method to compare.
        :return: True if the method aliases are different, False otherwise.
        """

        return not self.method == other_method.lower()

    def is_other_submethod(self, other_submethod: str) -> bool:
        """
        Checks if the subquery's submethod is different from another submethod.

        :param other_submethod: The other submethod to compare.
        :return: True if the submethods are different, False otherwise.
        """

        return not self.submethod == other_submethod.lower()

    def update_results(self, id: int, query_result: Any) -> dict:
        """
        Updates the results for the subquery.

        :param id: The id to update.
        :param query_result: The result to update.
        :return: The updated results.
        """

        if not self.is_id_in_subquery(id):

            return

        self._remove_processed_id(id)
        name = self.is_id_in_groups_by(id)

        if name:
            for group in self.results:
                if name in group:

                    group[name].append(query_result)

        else:
            self.results.append(query_result)

        return self.results

    def push_results(self, base_results: dict[str, dict]) -> Union[None, dict]:
        """
        Pushes the results to the base results.

        :param base_results: The base results to push to.
        :return: The updated base results.
        """

        if not self.is_processed_ids_complete():

            return
            
        base_results[self._method_alias][self._submethod] = self.results

        return base_results

    @property
    def method_alias(self) -> str:
        """
        Returns the method alias for the subquery.

        :return: The method alias as a string.
        """

        return self._method_alias

    @method_alias.setter
    def method_alias(self, new_method_alias: str) -> str:
        """
        Sets the method alias for the subquery.

        :param new_method_alias: The new method alias.
        :return: The updated method alias.
        """

        self._method_alias = new_method_alias.lower()

        return self._method_alias

    @property
    def submethod(self) -> str:
        """
        Returns the submethod for the subquery.

        :return: The submethod as a string.
        """

        return self._submethod

    @submethod.setter
    def submethod(self, new_submethod: str) -> str:
        """
        Sets the submethod for the subquery.

        :param new_submethod: The new submethod.
        :return: The updated submethod.
        """

        self._submethod = new_submethod.lower()

        return self._submethod