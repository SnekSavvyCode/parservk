from typing import Any

from .basehandler import BaseHandler


class UsersHandler(BaseHandler):

    def get_data_groups_subhandler(self, result):
        groups_items = result["groups"]["items"]

        return self.parser.groups.getById(group_ids=groups_items, ispool=True)

    def get_data_users_subhandler(self, result, name_handler="getsubscriptions"):
        if name_handler == "getfollowers":

            user_items = result["items"]

        elif name_handler == "getsubscriptions":

            user_items = result["users"]["items"]

        else:

            return []

        return self.parser.users.get(user_ids=user_items, ispool=True)

    def get_handler(self, result, id: int, **kwargs: Any):
        if not self.check_result(result):

            return []

        return result.json()["response"]

    def getsubscriptions_handler(self, result, id: int, **kwargs: Any):
        if not self.check_result(result):

            return []

        data_subscriptions = kwargs.get("data_subscriptions")
        result = result.json()["response"]

        if data_subscriptions:

            users = self.get_data_users_subhandler(
                result, name_handler="getsubscriptions"
            )
            groups = self.get_data_groups_subhandler(result)

            users_ids = self.poolmanager.add(users)
            groups_ids = self.poolmanager.add(groups)
            ids = users_ids + groups_ids

            return self.create_subquery(
                ids, groups_by=[{"users": users_ids, "groups": groups_ids}]
            )

        return result

    def getfollowers_handler(self, result, id: int, **kwargs: Any):
        if not self.check_result(result):

            return []

        data_followers = kwargs.get("data_followers")
        result = result.json()["response"]

        if data_followers:

            ids = self.poolmanager.add(
                self.get_data_users_subhandler(result, name_handler="getfollowers")
            )

            return self.create_subquery(ids)

        return result