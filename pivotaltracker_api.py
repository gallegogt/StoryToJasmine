#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
PivotalTracker API
"""

from urllib.request import Request, urlopen
from urllib import parse
import json

class PivotalTracker(object):
    """
    PivotalTracker Access Service
    """
    SERVICE_URL = 'https://www.pivotaltracker.com/services/v5/'
    API_PROJECT = SERVICE_URL + 'projects/'
    API_PROJECT_BY_ID = API_PROJECT + '{0}'
    API_PROJECT_STORY = API_PROJECT_BY_ID + '/stories/'
    API_PROJECT_STORY_BY_ID = API_PROJECT_STORY + '{1}'
    API_PROJECT_LABELS = API_PROJECT_BY_ID + '/labels'

    def __init__(self):
        """
        """
        #
        # @type {String}
        #
        self.__api_token = ''
        #
        # @type {Object}
        #
        self.__current_project = 0
        #
        # @type {Object[]}
        #
        self.__project_list = []

    @property
    def api_token(self):
        """
        Property Api Token
        """
        return self.__api_token

    @api_token.setter
    def api_token(self, token):
        """
        Property Api Token
        """
        self.__api_token = token

    @property
    def current_project(self):
        """
        Property Current Project
        """
        return self.__current_project

    @current_project.setter
    def current_project(self, project):
        """
        Property Current Project
        @param {Object} project
        """
        self.__current_project = project

    def get_service_data(self, url):
        """
        Retrieves data from service
        """
        req = Request(url)
        req.add_header('X-TrackerToken', self.__api_token)
        response = urlopen(req)
        data = response.read()
        return json.loads(data.decode('utf-8'))

    def post_service_data(self, url, data):
        """
        Retrieves data from service, POST
        """
        print(data)
        req = Request(url, data=data)
        req.add_header('X-TrackerToken', self.__api_token)
        req.add_header('Content-Type', 'application/json')

        response = urlopen(req)
        data = response.read()
        return json.loads(data.decode('utf-8'))

    def get_project_list(self, sync=False):
        """
        Retrieves all projects that can access
        @param sync     retrieve data form server
        @type Boolean
        """
        if sync or self.__project_list == []:
            self.__project_list = \
                self.get_service_data(PivotalTracker.API_PROJECT)
        return self.__project_list

    def get_project_info(self, project_id):
        """
        Retrieves project info by id
        """
        project = self.get_service_data(
            PivotalTracker.API_PROJECT_BY_ID.format(project_id))
        return project

    def get_story_list(self, project_id):
        """
        Retrieves all story by project id
        """
        story_list = self.get_service_data(
            PivotalTracker.API_PROJECT_STORY.format(project_id))
        return story_list

    def get_story_by_id(self, project_id, story_id):
        """
        Retrieves all story by project id
        """
        story_info = self.get_service_data(
            PivotalTracker.API_PROJECT_STORY_BY_ID.format(project_id, story_id))
        return story_info

    def get_story_list_by_labels(self, project_id, labels):
      """
      Get stoy by labels name
      """
      story_list = self.post_service_data(
        PivotalTracker.API_PROJECT_STORY.format(project_id),
        json.dumps({'labels': labels}))
      return story_list

    def get_label_list(self, project_id):
        """
        Retrieves all labels by project id
        """
        label_list = self.get_service_data(
            PivotalTracker.API_PROJECT_LABELS.format(project_id))
        return label_list
