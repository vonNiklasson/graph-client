import logging

import requests


class ServerUtil:

    base_url: str

    def __init__(self, base_url):
        if not base_url.endswith('/'):
            base_url = base_url + '/'
        self.base_url = base_url

    def get_task(self, client_name: str):
        url = "%sapi/thread" % self.base_url

        try:
            # Get the response from server
            response = requests.post(url, {'name': client_name})
        except Exception as e:
            logging.exception("Failed when fetching task")
            return None

        # Make sure it has created a resource
        if response.status_code == requests.codes.created:
            return response.json()
        else:
            return None

    def get_recalc_task(self):
        url = "%sapi/thread/recalc" % self.base_url

        try:
            # Get the response from server
            response = requests.get(url)
        except Exception as e:
            logging.exception("Failed when fetching recalc task")
            return None

        # Make sure it has created a resource
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            return None

    def upload_results(self, worker_id: int, data):
        url = "%sapi/thread/%d" % (self.base_url, worker_id)

        try:
            # Get the response from server
            response = requests.put(url, json=data)
        except Exception as e:
            logging.exception("Failed when uploading results")
            return False

        # Make sure it has created a resource
        if response.status_code == requests.codes.accepted:
            return True
        else:
            return False

    def close_previous_workers(self, client_name):
        url = '%sapi/workers/%s/close' % (self.base_url, client_name)
        requests.post(url)
