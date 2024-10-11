from typing import Any

from .basehandler import BaseHandler


class WallHandler(BaseHandler):
    
    def get_handler(self, result, id: int, **kwargs: Any):
        if not self.check_result(result):
            
            return []
            
        result = result.json()["response"]
        items = result["items"]

        if not self.is_subquery_id(id):
            max = result["count"] if kwargs.get("max") == "all" else kwargs.get("max")
            
            querys = self.parser.wall._paginate_querys(
                ids=[kwargs.get("owner_id")],
                method=self.name,
                submethod=self.method,
                params=kwargs.get("params"),
                min=kwargs.get("min"),
                max=max,
                count=kwargs.get("count"),
                multi_ids=kwargs.get("multi_ids"),
            )
             
            if len(querys):
                ids = self.poolmanager.add(querys)
            
                return self.create_subquery(
                ids, base_results=[(id, items)]
            )
               
        return items