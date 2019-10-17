#!/usr/bin/env python3
""" Update Rancher app answers using API """
import os
import requests


class RancherAPI:  # pylint: disable=too-few-public-methods
    """ Make calls to Rancher API """

    _CALLER = {
        'GET': requests.get,
        'PUT': requests.put,
        'POST': requests.post,
    }

    def __init__(self, api, token, check_ssl=True):
        self.api = api
        self.token = token
        self.headers = {
            'Authorization': "Bearer %s" % token,
            'Accept': 'application/json',
        }
        self.verify = check_ssl

    @staticmethod
    def _url_join(*args):
        return "/".join([a.strip('/') for a in args])

    def call(self, url='', method='get', data=None):
        """ Make an API call """
        method = method.upper()
        req = self._CALLER.get(method)
        url = url.replace(self.api, '')
        return req(
            self._url_join(self.api, url),
            headers=self.headers,
            json=data,
            verify=self.verify
        )

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)


class App:
    """ Represents an application installed inside Rancher """

    def __init__(self):
        self.ressource_id = ""
        self.name = ""
        self.answers = {}
        self.links = {}
        self.api: RancherAPI

    def update(self):
        """ Update the application with new answers """
        res = self.api(
            self.links.get('update'),
            method='put',
            data={'answers': self.answers}
        )
        return res

    def merge_answers(self, answers):
        """ Merge answers block with that new one """
        self.answers.update(answers)


class Project:  # pylint: disable=too-few-public-methods
    """ Represents a project in Rancher """

    def __init__(self):
        self.ressource_id = None
        self.links = []
        self.api: RancherAPI

    def app(self, name) -> App:
        """ Return Application that have this name """
        res = self.api(self.links.get('apps') + '?name=%s' % name)
        data = res.json().get('data')[0]
        app = App()
        app.ressource_id = data.get('id')
        app.name = data.get('name')
        app.answers = data.get('answers')
        app.links = data.get('links')
        return app


class Rancher:  # pylint: disable=too-few-public-methods
    """ Initial Rancher API class to get projects """

    def __init__(self, api='', token='', check_ssl='', cluster=''):
        self.ressource_id = None
        self.links = {}
        self.name = cluster
        self.api: RancherAPI = RancherAPI(api, token, check_ssl)

        self._init_links()

    def _init_links(self):
        cluster_url = self.api().json().get('links').get('clusters')
        res = self.api.call(cluster_url + '?name=' + self.name)
        data = res.json().get('data')[0]
        self.links = data.get('links')
        self.ressource_id = data.get('id')

    def project(self, name) -> Project:
        """ Return a Project having that name """
        call = self.links.get('projects') + '?name=%s' % name
        res = self.api.call(call)
        data = res.json().get('data')[0]

        prj = Project()
        prj.ressource_id = data.get('id')
        prj.links = data.get('links')
        prj.api = self.api
        return prj


def __main():

    api_url = os.environ.get('DRONE_PLUGIN_API')
    chek_ssl = os.environ.get('DRONE_PLUGIN_VERIFY', 'true') != 'false'
    project_name = os.environ.get('DRONE_PLUGIN_PROJECT', 'Default')
    app_name = os.environ.get('DRONE_PLUGIN_APP')
    cluster_name = os.environ.get('DRONE_PLUGIN_CLUSTER')
    token = os.environ.get('DRONE_PLUGIN_TOKEN', None)
    answer_keys = os.environ.get('DRONE_PLUGIN_KEYS', None).split(',')
    answer_values = os.environ.get('DRONE_PLUGIN_VALUES', None).split(',')

    rancher = Rancher(
        cluster=cluster_name,
        api=api_url,
        token=token,
        check_ssl=chek_ssl
    )
    project = rancher.project(project_name)
    app = project.app(app_name)
    answers = dict(zip(answer_keys, answer_values))
    app.merge_answers(answers)
    print(app.answers)
    print("Changing answers to", app.answers)
    app.update()


if __name__ == '__main__':
    __main()
