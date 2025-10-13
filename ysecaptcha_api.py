import requests
from typing import Union


class YesCaptchaApi:
    def __init__(self, api_key: str, id: str):
        self.api_key = api_key
        self.base_url = "https://api.yescaptcha.com"
        self.softID = id

    # 通用创建任务方法
    def create_task(self, type: str, **kwargs):
        pass

    # 通用获取识别结果
    def get_task_result(self, task_id: str) -> Union[str, None]:
        """
        Get the result of a task.

        :param task_id: The task ID.
        :return: The result of the task.
        """
        url = self.base_url + '/getTaskResult'
        payload = {
            "clientKey": self.api_key,
            "taskId": task_id
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        status = response.json()['status']
        if status == 'ready':
            return response.json()['solution']['token']
        else:
            return None

    # cf盾创建任务
    def create_cf_task(self, type: str, websiteURL: str, websiteKey: str) -> Union[str, None]:
        """
        Create a cf盾 task.

        :param type: The type of the task.
        :param websiteURL: The website URL.
        :param websiteKey: The website key.
        :return: The task ID.
        """
        url = self.base_url + '/createTask'
        payload = {
            "clientKey": self.api_key,
            "task": {
                "type": type,
                "websiteURL": websiteURL,
                "websiteKey": websiteKey
            },
            "softID": self.softID,
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['taskId']

    # CloudFlare5秒盾协议接口
    def create_cf_task_v5(self, type: str, websiteURL: str, proxy: str) -> str:
        """
        Create a cf盾 v5 task.

        :param type: The type of the task.
        :param websiteURL: The website URL.
        :param proxy: The proxy.
        :return: The task ID.
        """
        url = self.base_url + '/createTask'
        payload = {
            "clientKey": self.api_key,
            "task": {
                "type": type,
                "websiteURL": websiteURL,
                "proxy": proxy,
                "softID": self.softID

            }
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['data']['taskId']
