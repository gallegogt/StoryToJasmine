# StoryToJasmine

SublimeText plugin for BDD that retrieves a Story from Pivotaltracker and inserts it to the current document as a jasmine spec.

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

![Plugin options](https://www.dropbox.com/s/t2x2sc100gelmek/options.png?dl=1)

-- or --

Right click in the current buffer and select `Story to Jasmine` -> one of next options:

![Menu](https://www.dropbox.com/s/lofhzdfbt4ya7wu/contextMenu.png?dl=1)

**Pivotaltracker Story sample**

  ![PT Story](https://www.dropbox.com/s/8i1csnnc65mlrlv/pivotaltrackerStory.png?dl=1)


1. Set [Pivotaltracker Api Token](https://www.pivotaltracker.com/profile) (Api Token for access to the service)

  ![ApiToken](https://www.dropbox.com/s/bakp8lu7nutvwao/apitoken.png?dl=1)

2.- Set Project ID

  ![ProjectID](https://www.dropbox.com/s/02dxdw6b7i5ev80/projectid.png?dl=1)
  
3.- Get Story ID (This options is only for javascript files)

  ![StoryID](https://www.dropbox.com/s/71krbpftlr3gi96/storyid.png?dl=1)
  
*The result of last option is:*

  **Jasmine Code**

  ![Jasmine Code](https://www.dropbox.com/s/fbcmsbl2lmabz0s/jasmineCode.png?dl=1)


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


