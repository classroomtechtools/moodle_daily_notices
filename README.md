# moodle_daily_notices

Command line program that augments a database activity. 

## Getting Started

### Server side

#### Installation

Requires Python 3.6, as always with Python always use a virtual environment. I recommend [pyenv](https://github.com/pyenv/pyenv) with [virtualenv](https://github.com/pyenv/pyenv-virtualenv) plugin, and instructions using that follows

- pyenv install 3.6.0
- git clone https://github.com/classroomtechtools/moodle_daily_notices.git
- cd moodle_daily_notices
- pyenv virtualenv 3.6.0 moodle_daily_notices
- pyenv local moodle_daily_notices
- pip install -e .

#### Running

Entry point (at the moment) for outputing the emails is, this will not work unless Moodle side is also set up (below):

- notices notices launch teacher|student --email

Entry point (at the moment) for updating the "Start Date" and "End Date" fields is:

- notices notices launch teacher|student --update_date_fields

## Moodle side

Create a database activity, and note the name. That name needs to be input into the code in /notices/TeacherNotices.py line 20 or /notices/StudentNotices.py line 17 (the __init__ methods). The activity should have the following fields (name has to be exact):

![Fields Names and Types](http://url/to/img.png | width=100)

Note that start date and end date are NOT date fields but instead is a pop-up. The values are populated with the --update_date_fields command (above).

