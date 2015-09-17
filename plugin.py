#!/usr/bin/python
# -*- coding: utf-8 -*-

import sublime, sublime_plugin
from urllib.request import Request, urlopen
import json
import os

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
  def on_done(self, text):
    """
    Save Api Token in configuration file
    """
    PluginUtils.set_pref(KEY_API_TOKEN, text)

  def run(self, edit):
    # # show field to input to obtaining Api Token
    self.view.window().show_input_panel('PivotalTracker Api Token',
      '', self.on_done, None, None)


class StoryToJasmineProjectCommand(sublime_plugin.TextCommand):
  """
  Command charge of getting the ProjectID and save it
  """

  def on_done(self, text):
    """
    Save Api Token in configuration file
    """
    PluginUtils.set_pref(KEY_CURRENT_PROJECT, text)

  def run(self, edit):
    # show field to input to obtaining Project ID
    self.view.window().show_input_panel('Project Id',
      '', self.on_done, None, None)


class StoryToJasmineCommand(sublime_plugin.TextCommand):

  def on_done(self, story_text):

    story = PluginUtils.get_story(self.project_id, story_text, self.api_token)
    if story == None:
      return

    self.view.run_command(
      'story_to_jasmine_insert_text',
      {'args':
        {'description': story['description'],
          'story_id': story_text
        }
      })

  def run(self, edit):
    # if the file on the view is a javascript file continue
    file_name = self.view.file_name()
    if not file_name or not str(file_name).endswith(".js"):
        return

    self.project_id = PluginUtils.get_pref(KEY_CURRENT_PROJECT)
    self.api_token = PluginUtils.get_pref(KEY_API_TOKEN)
    # show field to input to obtaining Story ID
    self.view.window().show_input_panel('Story Id',
      '', self.on_done, None, None)


class StoryToJasmineInsertText(sublime_plugin.TextCommand):

  def run(self, edit, args):
    # add this to insert at current cursor position
    # http://www.sublimetext.com/forum/viewtopic.php?f=6&t=11509
    sp = StoryParser()
    rst = sp.parser(args['description'], args['story_id'])
    self.view.insert(edit, self.view.sel()[0].begin(), rst)

class PluginUtils:
  """
  Helper class
  """
  @staticmethod
  def get_pref(key):
    return sublime.load_settings(SETTINGS_FILE).get(key, '')

  @staticmethod
  def set_pref(key, value):
    return sublime.load_settings(SETTINGS_FILE).set(key, value)

  @staticmethod
  def open_sublime_settings(window):
    window.open_file(PLUGIN_FOLDER + "/" + SETTINGS_FILE)

  @staticmethod
  def get_story(projectID, storyID, apiToken):
    """
    Get back story on json format
    """
    if projectID == '' or storyID == '' or apiToken == '':
      return
    url = PIVOTAL_TRACKER_URL.format(projectID, storyID)
    req = Request(url)
    req.add_header('X-TrackerToken', apiToken)
    response = urlopen(req)
    data = response.read()
    return json.loads(data.decode('utf-8'))


class Singleton(type):
  """
  Singleton Class
  http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
  """
  _instances = {}
  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super(Singleton, cls).__call__(*args,
          **kwargs)
    return cls._instances[cls]


class StoryParser(object):
    """
    StoryParser
    """
    __metaclass__ = Singleton

    WITH_SPACE_LENGTH = 2

    def __init__(self):
      self.describe_list = []
      self.it_list = []
      self.word_Given = PluginUtils.get_pref('word_Given')
      self.word_And = PluginUtils.get_pref('word_And')
      self.word_When = PluginUtils.get_pref('word_When')
      self.word_Then = PluginUtils.get_pref('word_Then')
      self.it_template = PluginUtils.get_pref('it_template')
      self.describe_template = PluginUtils.get_pref('describe_template')

    def parser(self, story_text, story_id):
      description_list = story_text.split('\n')
      found_when = False
      for row in description_list:
        if row.startswith(self.word_Given):
          self.describe_list.append(row)
        elif row.startswith(self.word_And):
          if not found_when:
              self.describe_list.append(row)
          else:
              self.it_list.append(row)
        elif row.startswith(self.word_When):
          self.describe_list.append(row)
          found_when = True
        elif row.startswith(self.word_Then):
          self.it_list.append(row)

      its = self.proccesing_it_list(story_id, len(self.describe_list))
      desc = self.proccesing_describe_list()
      desc = desc % (its)
      self.describe_list = []
      self.it_list = []
      return desc

    def proccesing_describe_list(self):
      iterator = len(self.describe_list) - 1
      describe_rst = ''
      while(iterator >= 0):
        describe_text = self.describe_list[iterator]
        if iterator == (len(self.describe_list) - 1):
          describe_rst = self.describe_template.format(
            describe_text, '%s')
        else:
          _spaces = ' ' * ((iterator + 1) * self.WITH_SPACE_LENGTH)
          _last_spaces = ' ' * (iterator * self.WITH_SPACE_LENGTH)
          _str = '\n%s%s\n%s' % (_spaces,  describe_rst, _last_spaces)
          describe_rst = self.describe_template.format(describe_text,
              _str)
        iterator -= 1

      return describe_rst

    def proccesing_it_list(self, story_id, describe_len):
      """
      @return Javascript its text
      """
      it_text = '\n'
      for it in self.it_list:
        try:
          space = '%s' % (' ' * (describe_len * self.WITH_SPACE_LENGTH))
          it_text += space + self.it_template.format(it, story_id, '{}')
        except (ValueError, e):
          print(e)
      return it_text

