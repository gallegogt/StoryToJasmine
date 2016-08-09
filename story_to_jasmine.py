#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
SublimeText plugin for BDD that retrieves a Story from Pivotaltracker
and inserts it to the current document as a BDD spec.
"""

from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib import parse
import sys
from os.path import dirname as osDirname, realpath as osRealPath
from json import loads as jsonLoads
import sublime
import sublime_plugin

#
# Opciones de configuracion
#
# current_project: Identificador del proyecto
# pivotaltracker_api_token: Api Token
KEY_API_TOKEN = 'pivotaltracker_api_token'
KEY_CURRENT_PROJECT = 'current_project'

# ===================================================
#
# Plugin Utils
#
#====================================================

class PluginUtils(object):
    """Helper class

    Attributes:
        SETTINGS_FILE (str): Sublime settings file.
        PLUGIN_FOLDER (str): Plugin folder directory.
    """
    SETTINGS_FILE = 'StoryToJasmine.sublime-settings'
    PLUGIN_FOLDER = osDirname(osRealPath(__file__))

    @staticmethod
    def get_pref(key, default = '') -> str:
        """Get preferences from plugin settings file

        Args:
            key (str): key.

        Returns:
            The value of property key in the file. If the key not exist on
            settings file return empty string.
        """
        return sublime.load_settings(PluginUtils.SETTINGS_FILE).get(key, default)

    @staticmethod
    def set_pref(key, value):
        """Set preferences on plugin settings file

        Args:
            key (str): property to set in plugin settings file.
            value (str): value of the property key

        """
        sublime.load_settings(PluginUtils.SETTINGS_FILE).set(key, value)
        sublime.save_settings(PluginUtils.SETTINGS_FILE)

    @staticmethod
    def open_sublime_settings(window):
        """Open plugin settings file on new tab

        Args:
            window (Object): SublimeText Object
        """
        window.open_file(PluginUtils.PLUGIN_FOLDER + "/" + \
            PluginUtils.SETTINGS_FILE)

# ===================================================
#
# Story Parse
#
#====================================================

class StoryParse(object):
    """ Parse story and transform that story on BDD template

    Attributes:
        WITH_SPACE_LENGTH (integer): Space length.
    """
    WITH_SPACE_LENGTH = 2

    def __init__(self):
        """Initialize all class attributes
        """
        self.__describe_list = []
        self.__it_list = []
        self.__lang_tokens = {}

        self.__lang_tokens['word_given'] = \
            PluginUtils.get_pref('word_Given', ['Dado'])
        self.__lang_tokens['word_and'] = \
            PluginUtils.get_pref('word_And', ['Y'])
        self.__lang_tokens['word_when'] = \
            PluginUtils.get_pref('word_When', ['Cuando', 'Pero'])
        self.__lang_tokens['word_then'] = \
            PluginUtils.get_pref('word_Then', ['Entonces'])

        self.__lang_tokens['it_template'] = \
            PluginUtils.get_pref('it_template')
        self.__lang_tokens['describe_template'] = \
            PluginUtils.get_pref('describe_template')

    def parse(self, story_text, story_id) -> str:
        """Parse the story and transform with template text

        Args:
            story_text (str): story text to transform
            story_id (str): story id

        Returns:
        """
        description_list = story_text.split('\n')
        found_when = False
        check = lambda row, data: \
            len([w for w in data if row.startswith(w.strip() + ' ')]) > 0
        for row in description_list:
            if check(row, self.__lang_tokens.get('word_given')):
                self.__describe_list.append(row)
            elif check(row, self.__lang_tokens.get('word_and')):
                if not found_when:
                    self.__describe_list.append(row)
                else:
                    self.__it_list.append(row)
            elif check(row, self.__lang_tokens.get('word_when')):
                self.__describe_list.append(row)
                found_when = True
            elif check(row, self.__lang_tokens.get('word_then')):
                self.__it_list.append(row)

        its = self.proccesing_it_list(str(story_id), \
            len(self.__describe_list))
        desc = self.proccesing_describe_list()
        desc = desc % (its)
        self.__describe_list = []
        self.__it_list = []
        return desc

    def proccesing_describe_list(self) -> str:
        """Proccess describe_list converting that on Javascript code

        Returns:
            String
        """
        iterator = len(self.__describe_list) - 1
        describe_rst = ''
        while iterator >= 0:
            describe_text = self.__describe_list[iterator]
            if iterator == (len(self.__describe_list) - 1):
                describe_rst = \
                    self.__lang_tokens.get('describe_template').format(\
                        describe_text, '%s')
            else:
                _spaces = ' ' * ((iterator + 1) * self.WITH_SPACE_LENGTH)
                _last_spaces = ' ' * (iterator * self.WITH_SPACE_LENGTH)
                _str = '\n%s%s\n%s' % (_spaces, describe_rst, _last_spaces)
                describe_rst = \
                    self.__lang_tokens.get('describe_template') \
                        .format(describe_text, _str)
            iterator -= 1

        return describe_rst

    def proccesing_it_list(self, story_id, describe_len) -> str:
        """Processing it list

        Args:
            story_text (str): story id
            describe_len (str): length of describe list

        Returns:
            Javascript its text
        """
        it_text = '\n'

        if story_id[0] == '#':
            story_id = story_id[1:]

        for it_element in self.__it_list:
            try:
                space = '%s' % (' ' * (describe_len * self.WITH_SPACE_LENGTH))
                it_text += \
                    space + self.__lang_tokens.get('it_template') \
                        .format(it_element, story_id, '{\n' + \
                            space + '  }')
            except ValueError:
                pass
        return it_text


# ===================================================
#
# PivotalTracker Access Service
#
#====================================================

class PivotalTracker(object):
    """
    PivotalTracker Access Service

    Attributes:
        SERVICE_URL (str): Service URL.
        API_PROJECT (str): REST API URL for projects.
        API_PROJECT_BY_ID (str): REST API URL for projects by ID.
        API_PROJECT_STORY (str): REST API URL for stories.
        API_PROJECT_STORY_BY_ID (str): REST API URL for story by id.
        API_PROJECT_SEARCH (str): REST API URL for search.

    """
    SERVICE_URL = 'https://www.pivotaltracker.com/services/v5/'
    API_PROJECT = SERVICE_URL + 'projects/'
    API_PROJECT_BY_ID = API_PROJECT + '{0}'
    API_PROJECT_STORY = API_PROJECT_BY_ID + '/stories/'
    API_PROJECT_STORY_BY_ID = API_PROJECT_STORY + '{1}'
    API_PROJECT_SEARCH = API_PROJECT_BY_ID + '/search?query={1}'

    def __init__(self):
        """Initialize internal attributes

        Attributes:
            __api_token (str): User API token
            __current_project (object): Selected project
            __project_list (object[]): project list
        """
        self.__api_token = ''
        self.__current_project = None
        self.__project_list = []

    @property
    def api_token(self) -> str:
        """Property Api Token
        """
        return self.__api_token

    @api_token.setter
    def api_token(self, token):
        """Property Api Token

        Args:
            token (str): User token
        """
        self.__api_token = token

    @property
    def current_project(self):
        """Property Current Project

        Returns:
            Current project
        """
        return self.__current_project

    @current_project.setter
    def current_project(self, project):
        """Setter for current project property

        Args:
            project (object): new selected project
        """
        self.__current_project = project

    def get_service_data(self, url):
        """Retrieves data from service, GET method

        Args:
            url (str): URL

        Returns:
            JSON with service response
        """
        req = Request(url)
        req.add_header('X-TrackerToken', self.__api_token)
        response = urlopen(req)
        data = response.read()
        return jsonLoads(data.decode('utf-8'))

    def post_service_data(self, url, data):
        """Retrieves data from service, POST

        Args:
            url (str): URL
            data (str): string for send to server

        Returns:
            JSON with service response
        """
        data_to_send = parse.urlencode(data)
        data_received = None
        req = Request(url, data=data_to_send.encode('ascii'))
        req.add_header('X-TrackerToken', self.__api_token)
        req.add_header('Content-Type', 'application/json')
        try:
            with urlopen(req) as response:
                data_received = response.read()
        except HTTPError:
            return None

        return jsonLoads(data_received.decode('utf-8'))

    def get_project_list(self, sync=False):
        """Retrieves all projects that the user can access

        Args:
            sync (bool): if true retrieve the data from server, if false return
                the cache values

        Returns:
            Object list
        """
        if sync or self.__project_list == []:
            self.__project_list = \
                self.get_service_data(PivotalTracker.API_PROJECT)
        return self.__project_list

    def get_project_info(self, project_id):
        """Retrieves from server project info by id

        Args:
            project_id (:str:intiger): project id

        Returns:
            Object
        """
        project = self.get_service_data(
            PivotalTracker.API_PROJECT_BY_ID.format(project_id))
        return project

    def get_story_list(self, project_id):
        """Retrieves all story from server filter by project id

        Args:
            project_id (str,integer): project id

        Returns:
            Object
        """
        story_list = self.get_service_data(
            PivotalTracker.API_PROJECT_STORY.format(project_id))
        return story_list

    def get_story_by_id(self, project_id, story_id):
        """ Retrieves from server the story with id and project match
            with arguments

        Args:
            project_id (str): Project ID
            story_id (str): Story ID
        """
        story_info = self.get_service_data(
            PivotalTracker.API_PROJECT_STORY_BY_ID.format(project_id, story_id))
        return story_info

    def search_in_project(self, project_id, query):
        """Retrieves data from service that match with the query

        Args:
            project_id (str): Project ID
            query (str): Story ID
        """
        url = PivotalTracker.API_PROJECT_SEARCH.format(project_id, \
            parse.quote_plus(query))
        return self.get_service_data(url)


# ===================================================
#
# Singleton
#
#====================================================

class Singleton(type):
    """
    Singleton Class
    http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Function __call__

        Args:
            *args (list): argument list
            **kwargs (dict): argument dict
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, \
                    **kwargs)
        return cls._instances[cls]


# ===================================================
#
# Sublime To BDD
#
#====================================================

class StoryToBDD(metaclass=Singleton):
    """
    Story To Jasmine
    """
    def __init__(self):
        """Initialize internals attributes

        Attributes:
            __service_access (object): service access object
            __stories_cache (list): stories cache
        """
        self.__service_access = PivotalTracker()
        self.__stories_cache = []
        self.__story_parse = StoryParse()

    def load_default_values(self):
        """Load default values from plugin settings
        """
        self.__service_access.api_token = \
            PluginUtils.get_pref(KEY_API_TOKEN)
        current_project_id = PluginUtils.get_pref(KEY_CURRENT_PROJECT)
        if current_project_id != '':
            self.__service_access.current_project = current_project_id

    def get_current_project(self):
        """Get current project object

        Returns
            Object
        """
        return self.__service_access.current_project

    def set_api_token(self, api_token):
        """Set user API Token and update plugin preferences value

        Args:
            api_token (str): token
        """
        self.__service_access.api_token = api_token
        #
        # Update api token on plugin settings
        #
        PluginUtils.set_pref(KEY_API_TOKEN, api_token)

    def sync_project_from_service(self):
        """Retirieve all project from server

        Returns:
            List of projects name
        """
        p_list = self.__service_access.get_project_list(True)
        return [project['name'] for project in p_list]

    def set_default_project(self, index):
        """Set project by index as default

        Args:
           index (integer): index of project
        """
        if index == -1:
            return
        p_list = self.__service_access.get_project_list()
        self.__service_access.current_project = p_list[index]

    def set_default_project_by_id(self, project_id):
        """Set project by index as default

        Args:
           project_id (integer,str): project id
        """
        p_list = self.__service_access.get_project_list(True)
        project = [project for project in p_list if project['id'] == project_id]
        if len(project) > 0:
            self.__service_access.current_project = project[0]
        else:
            self.__service_access.current_project = {'id': project_id}
        #
        # Update current project id on plugin settings
        #
        PluginUtils.set_pref(KEY_CURRENT_PROJECT, project_id)

    def get_story_list(self):
        """Get all story from selected project

        Returns:
            list of story names
        """
        current_project = self.get_current_project()
        if current_project != None:
            self.__stories_cache = \
                self.__service_access.get_story_list(current_project['id'])

        return [story['name'] for story in self.__stories_cache]

    def get_story_by_id(self, story_id):
        """Retrieve story from server

        Args:
            story_id (str): story id

        Returns:
            Object or None
        """
        current_project = self.get_current_project()
        if current_project != None:
            return self.__service_access.get_story_by_id(\
                current_project['id'], story_id)

        return None

    def get_stories_in_cache(self):
        """Get all stories cached

        Returns:
            List of story cached
        """
        return self.__stories_cache

    def get_stories_by_search(self, query):
        """Get stories by labels name

        Args:
            query (str): query

        Returns:
            List of story objects
        """
        current_project = self.get_current_project()
        if current_project != None:
            query_result = self.__service_access.search_in_project(
                current_project['id'], query)
            self.__stories_cache = query_result['stories']['stories']
        return self.__stories_cache

    def get_code(self, story_desc, story_id) -> str:
        """Get the code deribed of story description

        Args:
            story_desc (str): story description
            story_id (str): story description

        Returns:
            String
        """
        return self.__story_parse.parse(story_desc, story_id)


# ===================================================
#
# Sublime Commands
#
#====================================================

story_to_bdd = StoryToBDD()

class StoryToJasmineApitokenCommand(sublime_plugin.TextCommand):
    """Command charge of getting the Api Token and save it
    """
    @staticmethod
    def on_done(token):
        """Save Api Token in configuration file

        Args:
            token (str): API token
        """
        story_to_bdd.set_api_token(token)

    def run(self, edit):
        """Main function on text command

        Args:
            edit (object): sublime text object
        """
        # show field to input to obtaining Api Token
        self.view.window().show_input_panel('PivotalTracker Api Token', \
            '', self.on_done, None, None)


class StoryToJasmineProjectCommand(sublime_plugin.TextCommand):
    """Command charge of getting the ProjectID and save it
    """
    @staticmethod
    def on_done(project_id):
        """Save project id

        Args:
            project_id (str): project id
        """
        story_to_bdd.set_default_project_by_id(project_id)

    def run(self, edit):
        """Main function on text command

        Args:
            edit (object): sublime text object
        """
        # show field to input to obtaining Project ID
        self.view.window().show_input_panel('Project Id', \
                '', self.on_done, None, None)


class StoryToJasmineCommand(sublime_plugin.TextCommand):
    """Text command to get story
    """
    def on_done(self, story_id):
        """This function get the story

        Args:
            story_id (str): story id
        """
        s_id = story_id
        if story_id[0] == '#':
            s_id = story_id[1:]
        story = story_to_bdd.get_story_by_id(s_id)
        if story != None:
            self.view.run_command(
                'story_to_jasmine_insert_text', \
                {'args': {'description': story['description'], \
                            'story_id': story_id}})

    def run(self, edit):
        """Main function on text command

        Args:
            edit (object): sublime text object
        """
        # if the file on the view is a javascript file continue
        file_name = self.view.file_name()
        if not file_name or not str(file_name).endswith(".js"):
            return
        # show field to input to obtaining Story ID
        self.view.window().show_input_panel('Story Id', \
                '', self.on_done, None, None)


class StoryToJasmineInsertText(sublime_plugin.TextCommand):
    """TextCommand to insert the jasmine code into edited file
    """
    def run(self, edit, args):
        """Main function on text command

        Args:
            edit (object): sublime text object
            args (object): object with two properties (description and story_id)
        """
        # add this to insert at current cursor position
        # http://www.sublimetext.com/forum/viewtopic.php?f=6&t=11509
        print(args)
        code = story_to_bdd.get_code(args['description'], args['story_id'])
        self.view.insert(edit, self.view.sel()[0].begin(), code)


class StoryToJasmineOptionsCommand(sublime_plugin.TextCommand):
    """TextCommand for open plugins settings
    """
    def run(self, edit):
        """Main function on text command

        Args:
            edit (object): sublime text object
        """
        PluginUtils.open_sublime_settings(self.view.window())


class StoryToJasmineSelectProjectFromListCommand(sublime_plugin.TextCommand):
    """Select project from list
    """
    @staticmethod
    def on_select(project_index):
        """This function get the story

        Args:
            project_index (str): selected project index
        """
        story_to_bdd.set_default_project(project_index)

    def run(self, edit):
        """Main function

        Args:
            edit (object): sublime text object
        """
        project_list = story_to_bdd.sync_project_from_service()
        self.view.window().show_quick_panel(project_list, self.on_select)


class StoryToJasmineSearchCommand(sublime_plugin.TextCommand):
    """
    Search Command

    Execute from ST console:
        view.run_command('story_to_jasmine_search')
    """
    def on_select_query(self, story_index):
        """
        This function get the story
        @param {Integer} story_index
        """
        if story_index >= 0:
            story = story_to_bdd.get_stories_in_cache()[story_index]
            self.view.run_command(
                'story_to_jasmine_insert_text', \
                {'args': { \
                    'description': story['description'], \
                    'story_id': story['id'] \
                    } \
                } \
            )

    def on_done(self, search):
        """This function get the story

        Args:
            search (str): search query
        """
        s_list = story_to_bdd.get_stories_by_search(search)
        self.view.window().show_quick_panel( \
            [story['name'] for story in s_list], \
            self.on_select_query)


    def run(self, edit):
        """Main function

        Args:
            edit (object): sublime text object
        """
        # if the file on the view is a javascript file continue
        file_name = self.view.file_name()
        if file_name and str(file_name).endswith(".js"):
            # show field to input to obtaining Story ID
            self.view.window().show_input_panel('Search story', \
                    '', self.on_done, None, None)


class StoryToJasmineTestCommand(sublime_plugin.TextCommand):
    """ Comand for test
    """
    def on_select(self):
        """ This function get the story
        """
        pass

    def run(self, edit):
        """
        Main function
        """
        story_to_bdd.set_api_token('API_TOKEN')

        story_to_bdd.set_default_project(0)
        s_list = story_to_bdd.get_stories_by_search('label:issue-1797')
        self.view.window().show_quick_panel(
            [story['name'] for story in s_list], self.on_select)


def plugin_loaded():
    """ When the script is loaded, the default values are loaded
    """
    story_to_bdd.load_default_values()
    print('Plugin loaded.....!!!')

def plugin_unloaded():
    """ When the script is unloaded
    """
    pass

# Compat with ST2
if sys.version_info < (3,):
    plugin_loaded()
    unload_handler = plugin_unloaded
