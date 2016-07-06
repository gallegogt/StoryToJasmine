#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
SublimeText plugin for BDD that retrieves a Story from Pivotaltracker
and inserts it to the current document as a jasmine spec.
"""
# pylint: disable=too-few-public-methods, superfluous-parens, too-many-instance-attributes, no-init

import sublime, sublime_plugin
from urllib.request import Request, urlopen
from .s2j import S2J, Singleton

import json
import os
import re

#
# Opciones de configuracion
#
# current_project: Identificador del proyecto
# pivotaltracker_api_token: Api Token

PLUGIN_FOLDER = os.path.dirname(os.path.realpath(__file__))
SETTINGS_FILE = 'StoryToJasmine.sublime-settings'
PIVOTAL_TRACKER_URL = \
  'https://www.pivotaltracker.com/services/v5/projects/{0}/stories/{1}'
KEY_API_TOKEN = 'pivotaltracker_api_token'
KEY_CURRENT_PROJECT = 'current_project'


class StoryToJasmineApitokenCommand(sublime_plugin.TextCommand):
    """
    Command charge of getting the Api Token and save it
    """
    @staticmethod
    def on_done(text):
        """
        Save Api Token in configuration file
        """
        story2jasmine = S2J()
        story2jasmine.set_api_token(text)
        PluginUtils.set_pref(KEY_API_TOKEN, text)

    def run(self, edit):
        """
        Main function on text command
        """
        # show field to input to obtaining Api Token
        self.view.window().show_input_panel('PivotalTracker Api Token', \
                '', self.on_done, None, None)


class StoryToJasmineProjectCommand(sublime_plugin.TextCommand):
    """
    Command charge of getting the ProjectID and save it
    """
    @staticmethod
    def on_done(project_id):
        """
        Save Api Token in configuration file
        """
        PluginUtils.set_pref(KEY_CURRENT_PROJECT, project_id)

        story_to_jasmine = S2J()
        story_to_jasmine.set_default_project_by_id(project_id)

    def run(self, edit):
        """
        Main function on text command
        """
        # show field to input to obtaining Project ID
        self.view.window().show_input_panel('Project Id', \
                '', self.on_done, None, None)


class StoryToJasmineCommand(sublime_plugin.TextCommand):
    """
    Text command to get story
    """
    def on_done(self, story_text):
        """
        This function get the story
        """
        story = PluginUtils.get_story(self.project_id, story_text, \
            self.api_token)
        if story == None:
            return

        self.view.run_command(
            'story_to_jasmine_insert_text', \
            {'args': {'description': story['description'], \
                        'story_id': story_text}})

    def run(self, edit):
        """
        Main function on text command
        """
        # if the file on the view is a javascript file continue
        file_name = self.view.file_name()
        if not file_name or not str(file_name).endswith(".js"):
            return

        self.project_id = PluginUtils.get_pref(KEY_CURRENT_PROJECT)
        self.api_token = PluginUtils.get_pref(KEY_API_TOKEN)
        # show field to input to obtaining Story ID
        self.view.window().show_input_panel('Story Id', \
                '', self.on_done, None, None)


class StoryToJasmineInsertText(sublime_plugin.TextCommand):
    """
    TextCommand to insert the jasmine code into edited file
    """
    def run(self, edit, args):
        """
        Main function on text command
        """
        # add this to insert at current cursor position
        # http://www.sublimetext.com/forum/viewtopic.php?f=6&t=11509
        story_parser = StoryParser()
        rst = story_parser.parser(args['description'], args['story_id'])
        self.view.insert(edit, self.view.sel()[0].begin(), rst)


class StoryToJasmineOptionsCommand(sublime_plugin.TextCommand):
    """
    TextCommand for open plugins settings
    """
    def run(self, edit):
        """
        Main function on text command
        """
        PluginUtils.open_sublime_settings(self.view.window())


class StoryToJasmineSelectProjectFromListCommand(sublime_plugin.TextCommand):
    """
    Select project from list
    """
    def on_select(self, project_index):
        """
        This function get the story
        """
        self.__story_to_jasmine.set_default_project(project_index)

    def run(self, edit):
        """
        Main function
        """
        self.__story_to_jasmine = S2J()
        project_list = self.__story_to_jasmine.get_project_list()
        self.view.window().show_quick_panel(project_list, self.on_select)


class StoryToJasmineTestCommand(sublime_plugin.TextCommand):
    """
    Comand for test
    """
    def on_select(self, index):
        """
        This function get the story
        """
        #story_to_jasmine = S2J()
        #story_to_jasmine.set_default_project(project_index)
        #story_to_jasmine.set_default_project_by_id(96519)
        print(index)

    def run(self, edit):
        """
        Main function
        """
        story_to_jasmine = S2J()
        story_to_jasmine.set_api_token('0d9fd4710ca1de1395e05ec0e3953f2d')

        story_to_jasmine.set_default_project(0)

        s_list = story_to_jasmine \
            .get_stories_by_labels_name('agenda,sobreagenda')
        print(s_list)
        self.view.window().show_quick_panel(
            [story['name'] for story in s_list], self.on_select)


class PluginUtils(object):
    """
    Helper class
    """
    @staticmethod
    def get_pref(key):
        """
        @brief Get preferences

        @param key
        @return string
        """
        return sublime.load_settings(SETTINGS_FILE).get(key, '')

    @staticmethod
    def set_pref(key, value):
        """
        @brief Set preferences

        @param key
        @param value
        """
        return sublime.load_settings(SETTINGS_FILE).set(key, value)

    @staticmethod
    def open_sublime_settings(window):
        """
        @brief Open sublime settings

        @param window
        """
        window.open_file(PLUGIN_FOLDER + "/" + SETTINGS_FILE)

    @staticmethod
    def get_story(project_id, story_id, api_token):
        """
        @brief Get back story on json format

        @param project_id
        @param story_id
        @param api_token
        @return JSON
        """
        if project_id == '' or story_id == '' or api_token == '':
            return
        # if story contains leading '#' remove it
        story_id = re.sub('^#', '', story_id)
        url = PIVOTAL_TRACKER_URL.format(project_id, story_id)
        req = Request(url)
        req.add_header('X-TrackerToken', api_token)
        response = urlopen(req)
        data = response.read()
        return json.loads(data.decode('utf-8'))

class StoryParser(object):
    """
    StoryParser
    """
    __metaclass__ = Singleton

    WITH_SPACE_LENGTH = 2

    def __init__(self):
        """
        Constructor
        """
        self.describe_list = []
        self.it_list = []
        self.word_given = PluginUtils.get_pref('word_Given').strip() + ' '
        self.word_and = PluginUtils.get_pref('word_And').strip() + ' '
        self.word_when = PluginUtils.get_pref('word_When').strip() + ' '
        self.word_then = PluginUtils.get_pref('word_Then').strip() + ' '
        self.it_template = PluginUtils.get_pref('it_template')
        self.describe_template = PluginUtils.get_pref('describe_template')

    def parser(self, story_text, story_id):
        """
        Function to parser the story text and convert it on
        jasmine code
        """
        description_list = story_text.split('\n')
        found_when = False
        for row in description_list:
            if row.startswith(self.word_given):
                self.describe_list.append(row)
            elif row.startswith(self.word_and):
                if not found_when:
                    self.describe_list.append(row)
                else:
                    self.it_list.append(row)
            elif row.startswith(self.word_when):
                self.describe_list.append(row)
                found_when = True
            elif row.startswith(self.word_then):
                self.it_list.append(row)

        its = self.proccesing_it_list(story_id, len(self.describe_list))
        desc = self.proccesing_describe_list()
        desc = desc % (its)
        self.describe_list = []
        self.it_list = []
        return desc

    def proccesing_describe_list(self):
        """
        Aux function to proccess  describe_list converting that on
        Javascript code

        @return describe template
        """
        iterator = len(self.describe_list) - 1
        describe_rst = ''
        while (iterator >= 0):
            describe_text = self.describe_list[iterator]
            if iterator == (len(self.describe_list) - 1):
                describe_rst = self.describe_template.format( \
                        describe_text, '%s')
            else:
                _spaces = ' ' * ((iterator + 1) * self.WITH_SPACE_LENGTH)
                _last_spaces = ' ' * (iterator * self.WITH_SPACE_LENGTH)
                _str = '\n%s%s\n%s' % (_spaces, describe_rst, _last_spaces)
                describe_rst = self.describe_template.format(describe_text, \
                        _str)
            iterator -= 1

        return describe_rst

    def proccesing_it_list(self, story_id, describe_len):
        """
        Processing it list

        @param story_id
        @param describe_len
        @return Javascript its text
        """
        it_text = '\n'

        if story_id[0] == '#':
            story_id = story_id[1:]

        for it_element in self.it_list:
            try:
                space = '%s' % (' ' * (describe_len * self.WITH_SPACE_LENGTH))
                it_text += space + self.it_template.format(it_element, \
                    story_id, '{}')
            except (ValueError):
                pass
        return it_text
