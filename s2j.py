#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Sublime To Jasmine Logic
"""
from .pivotaltracker_api import PivotalTracker

class Singleton(type):
    """
    Singleton Class
    http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        """
        __call__

        @param *args
        @param **kwargs
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, \
                    **kwargs)
        return cls._instances[cls]


class S2J(metaclass=Singleton):
    """
    Story To Jasmine
    """
    def __init__(self):
        """
        Constructor
        """
        self.__data_access = PivotalTracker()
        self.__stories_cache = []

    def get_current_project(self):
        """
        @return {Object}
        """
        return self.__data_access.current_project

    def set_api_token(self, api_token):
        """
        @param {String} api_token
        """
        self.__data_access.api_token = api_token
        #
        # force to retrieve data from server
        #
        self.__data_access.get_project_list(True)

    def get_project_list(self):
        """
        @return project list as string
        """
        p_list = self.__data_access.get_project_list()
        return [project['name'] for project in p_list]

    def set_default_project(self, index):
        """
        Set project by index as default

        @param {Integer} index
        """
        if index == -1:
            return
        p_list = self.__data_access.get_project_list()
        self.__data_access.current_project = p_list[index]

    def set_default_project_by_id(self, project_id):
        """
        Set project by index as default

        @param {Integer} index
        """
        p_list = self.__data_access.get_project_list()
        project = [project for project in p_list if project['id'] == project_id]
        self.__data_access.current_project = project[0]

    def get_story_list(self):
        """
        Get story list
        """
        current_project = self.get_current_project()
        s_list = []
        if current_project != None:
            s_list = self.__data_access.get_story_list(current_project['id'])
        return [story['name'] for story in s_list]

    def get_label_list(self):
        """
        """
        current_project = self.get_current_project()
        s_list = []
        if current_project != None:
            s_list = self.__data_access.get_label_list(current_project['id'])
        return [label['name'] for label in s_list]

    def get_stories_in_cache(self):
        """
        """
        return self.__stories_cache;

    def get_stories_by_labels_name(self, labels):
        """
        """
        current_project = self.get_current_project()
        label_list = labels.strip().split(',')
        if current_project != None and len(label_list) > 0:
            self.__stories_cache = \
                self.__data_access.get_story_list_by_labels(
                    current_project['id'], label_list)
        return self.__stories_cache

