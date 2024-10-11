from typing import Any

from .basehandler import BaseHandler


class FriendsHandler(BaseHandler):

    def get_handler(self, result, id: int, **kwargs: Any):
        if not self.check_result(result):

            return []

        data_friends = kwargs.get("data_friends")
        items = result.json()["response"]["items"]

        if data_friends:

            querys = self.parser.users.get(user_ids=items, ispool=True)
            ids = self.poolmanager.add(querys)

            return self.create_subquery(ids)

        return items