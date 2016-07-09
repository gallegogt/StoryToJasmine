# StoryToJasmine

SublimeText plugin for BDD that retrieves a Story from Pivotaltracker and inserts it to the current document as a jasmine spec.


# New FEATURES!!!!!!

* Can select project from list after set the Pivotaltracker Id (`Ctrl+Shift+P` `Story to Jasmine: Select project from list`)

  **Project list on sublime**
  ![SJ Project from list](https://www.dropbox.com/s/29mvq51m3ji9lds/st_select_project_from_list.png?dl=1)


  **Pivotaltracker project list**
  ![Pivotaltracker project list](https://www.dropbox.com/s/ia0yslaf04639cd/pt_project_list.png?dl=1)


* After select the project now can you use "search operator" to select stories (`Ctrl+Shift+P` `Story to Jasmine: Search story`). It use the same sintax that Pivotaltracker site.


  **Search story by type:feature**
  ![SJ Project from list](https://www.dropbox.com/s/eu3zbuxmavvxul3/st_search_story.png?dl=1)


  **Search on sublime**
  ![SJ Project from list](https://www.dropbox.com/s/9xyban4di827du5/st_search_result.png?dl=1)


  **Pivotaltracker search result**
  ![Pivotaltracker project list](https://www.dropbox.com/s/ua72yy0d2e93obt/pt_search_result.png?dl=1)


  **Pivotaltracker sintax**

  ![Pivotaltracker project list](https://www.dropbox.com/s/n01977ymtb4lndl/pt_search_operators.png?dl=1)


## Installation

The shorter way of doing this is (Not yet):
### Through [Sublime Package Manager](https://packagecontrol.io)

* `Ctrl+Shift+P` or &#8984;`+Shift+P` in Linux/Windows/OS X
* type `install`, select `Package Control: Install Package`
* type and select `StorytoJasmine`
 

### Manually

Make sure you use the right Sublime Text folder. For example, on OS X, packages for version 2 are in `~/Library/Application\ Support/Sublime\ Text\ 2`, while version 3 is labeled `~/Library/Application\ Support/Sublime\ Text\ 3`.

These are for Sublime Text 3:

#### Mac
`git clone https://github.com/gallegogt/StoryToJasmine.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/StoryToJasmine`

#### Linux
`git clone https://github.com/gallegogt/StoryToJasmine.git ~/.config/sublime-text-3/Packages/StoryToJasmine`

#### Windows
`git clone https://github.com/gallegogt/StoryToJasmine.git "%APPDATA%/Sublime Text 3/Packages/StoryToJasmine"`


## Usage

Tools -> Command Palette (`Ctrl+Shift+P` or &#8984;+Shift+P`) and type `Story to Jasmine`.

![Plugin options](https://www.dropbox.com/s/8bw8hd4tm53zawa/st_plugin_options.png?dl=1)

-- or --

Right click in the current buffer and select `Story to Jasmine` -> one of next options:

![Menu](https://www.dropbox.com/s/q6o5ixxcs90197w/st_context_menu.png?dl=1)

**Pivotaltracker Story sample**

  ![PT Story](https://www.dropbox.com/s/idu8pcouwdngq7z/pt_story.png?dl=1)


1. Set [Pivotaltracker Api Token](https://www.pivotaltracker.com/profile) (Api Token for access to the service)

  ![ApiToken](https://www.dropbox.com/s/suuwfw800i1i95k/pt_api_token.png?dl=1)

2.- Set Project Id

  **Project id on pivotaltracker site**

  ![Project id on Pivotaltracker site](https://www.dropbox.com/s/5jsoxsagdpx579f/pt_project_id.png?dl=1)

  **Set project id on sublime**
  ![Set project id on sublime](https://www.dropbox.com/s/ly5oi3s14gtjo17/st_select_project_id.png?dl=1)
  
3.- Get Story ID (This options is only for javascript files)

  **Story id on pivotaltracker site**
  ![StoryID](https://www.dropbox.com/s/nzm1hxn2yym4kqv/pt_story%20id.png?dl=1)

  **Set this story id on ST plugin**
  ![StoryID](https://www.dropbox.com/s/jrlj7j4y1gmgiaq/st_select_story.png?dl=1)
  
*The result of last option is:*

  **Jasmine Code**

  ![Jasmine Code](https://www.dropbox.com/s/q4bhqfwo97hmwt6/st_story_result.png?dl=1)


## Settings

Tools -> Story to Jasmine -> Set Plugin Options

```json
{
  // default current project
  "current_project": "",

  // default PivotalTracker Api Token
  "pivotaltracker_api_token": "",

  // story keywords (change the keywords values for other languages)
  "word_Given": "Dado ",
  "word_And": "Y ",
  "word_When": "Cuando ",
  "word_Then": "Entonces ",

  // jasmine simple template
  "describe_template": "describe('{0}', function() {{{1}}});",
  "it_template": "it('{0} [ID:#{1}]', function() {2});\n\n"
}
```


## Operating Systems

This package works on Windows, OSX, and Linux


