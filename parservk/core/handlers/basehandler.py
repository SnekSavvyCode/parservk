from typing import Any, Union, Optional

from .subquery import SubQuery


class BaseHandler:
    skipped_handlers = ["main_handler"]
    
    RE_URL_API = r"https?://api.vk.com/method/"

    def __init__(self, poolmanager, parser, handlers) -> None:
        self._result = []
        self._subquerys_ids = []
        self.subquerys = []
        self.poolmanager = poolmanager
        self.parser = parser
        self.handlers = handlers
        self.method = None
        self.name = self.get_name(self)
        self._submethods_handler = self.handlers.create_submethods(self.name, self.skipped_handlers)

    @staticmethod
    def get_name(obj: object) -> str:
        name = getattr(obj, '__name__', obj.__class__.__name__)
        

        return name.lower().replace("handler", "")

    @staticmethod
    def get_method(url: str) -> str:

        return url.split(".")[-1].lower()

    @staticmethod
    def get_response_body(result: str) -> dict:
        return dict(element.split("=") for element in result.request.body.split("&"))

    @staticmethod
    def check_result(result, passed_exception: list = []) -> bool:
        try:

            result.raise_for_status()
            
            if not "error" in result.json():
            	
            	return True
            	
        except Exception as e:
            pass
        
        return False
    
    def create_subquery(
        self,
        ids: list[int],
        path_subquery: Optional[str] = None,
        params: dict = {},
        base_results=None,
        groups_by=None,
    ) -> SubQuery:
        self._subquerys_ids.extend(ids)
        path_subquery = path_subquery or f"{self.name}.{self.method}"
        subquery = SubQuery(ids, path_subquery, params, base_results, groups_by)
        self.subquerys.append(subquery)

        return subquery

    def is_subquery_id(self, id: int) -> bool:
    	return id in self._subquerys_ids

    def main_handler(self, result, id: int, **kwargs: Any) -> Any:

        self.method = self.get_method(result.url)
        self.result_query = result

        handler = self._submethods_handler.get(self.method)
        if not handler is None:
            
            return handler(self, self.result_query, id=id, **kwargs)