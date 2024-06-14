import os
from pocketbase import PocketBase  # Client also works the same
from pocketbase.client import FileUpload
from typing import BinaryIO


class PbTalker:
    def __init__(self, logger) -> None:
        # 1. base initialization
        url = "http://127.0.0.1:5882"
        self.logger = logger
        self.logger.debug(f"initializing pocketbase client: {url}")
        self.client = PocketBase(url)
        auth = os.environ.get('PB_API_AUTH', '')
        if not auth or "|" not in auth:
            self.logger.warnning("invalid email|password found, will handle with not auth, make sure you have set the collection rule by anyone")
        else:
            email, password = auth.split('|')
            try:
                admin_data = self.client.admins.auth_with_password(email, password)
                if admin_data:
                    self.logger.info(f"pocketbase ready authenticated as admin - {email}")
            except:
                user_data = self.client.collection("users").auth_with_password(email, password)
                if user_data:
                    self.logger.info(f"pocketbase ready authenticated as user - {email}")
                else:
                    raise Exception("pocketbase auth failed")

    def read(self, collection_name: str, fields: list[str] = None, filter: str = '', skiptotal: bool = True) -> list:
        results = []
        for i in range(1, 10):
            try:
                res = self.client.collection(collection_name).get_list(i, 500,
                                                                       {"filter": filter,
                                                                        "fields": ','.join(fields) if fields else '',
                                                                        "skiptotal": skiptotal})

            except Exception as e:
                self.logger.error(f"pocketbase get list failed: {e}")
                continue
            if not res.items:
                break
            for _res in res.items:
                attributes = vars(_res)
                results.append(attributes)
        return results

    def add(self, collection_name: str, body: dict) -> str:
        try:
            res = self.client.collection(collection_name).create(body)
        except Exception as e:
            self.logger.error(f"pocketbase create failed: {e}")
            return ''
        return res.id

    def update(self, collection_name: str, id: str, body: dict) -> str:
        try:
            res = self.client.collection(collection_name).update(id, body)
        except Exception as e:
            self.logger.error(f"pocketbase update failed: {e}")
            return ''
        return res.id

    def delete(self, collection_name: str, id: str) -> str:
        try:
            res = self.client.collection(collection_name).delete(id)
        except Exception as e:
            self.logger.error(f"pocketbase update failed: {e}")
            return 'failed'
        if res:
            return 'success'
        return 'failed'

    def upload(self, collection_name: str, id: str, key: str, file_name: str, file: BinaryIO) -> str:
        try:
            res = self.client.collection(collection_name).update(id, {key: FileUpload((file_name, file))})
        except Exception as e:
            self.logger.error(f"pocketbase update failed: {e}")
            return ''
        return res.id

    def view(self, collection_name: str, item_id: str, fields: list[str] = None) -> dict:
        try:
            res = self.client.collection(collection_name).get_one(item_id,{"fields": ','.join(fields) if fields else ''})
            return vars(res)
        except Exception as e:
            self.logger.error(f"pocketbase view item failed: {e}")
            return {}
