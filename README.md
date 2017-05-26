# moodle_daily_notices

Command line program that augments a database activity. 

## Getting Started

### Server side

#### Installation

Requires Python 3.6, as always with Python always use a virtual environment. I recommend [pyenv](https://github.com/pyenv/pyenv) with [virtualenv](https://github.com/pyenv/pyenv-virtualenv) plugin, and instructions using that follows

1. `pyenv install 3.6.0`
1. `git clone https://github.com/classroomtechtools/moodle_daily_notices.git`
1. `cd moodle_daily_notices`
1. `pyenv virtualenv 3.6.0 moodle_daily_notices`
1. `pyenv local moodle_daily_notices`
1. `pip install -e .`

You should then see output indicating that the software has been installed into the virtualenv. 

##### Upgrading

If improvements are made then you may wish to update the software:

1. `cd /path/to/moodle_daily_notices`
1. `git pull origin master`
1. `pip install -e .`

#### Setup

You need to have a settings.ini file with the appropriate content.

1. `cd /path/to/moodle_daily_notices`
1. `cp settings_default.ini settings.ini`
1. `nano settings.ini`
1. (edit the file according to your needs)

There is a place for student and teacher notices, but you could have just one if desired. The "db_activity" attributes have to coorespond to the database activity created on the Moodle side. 

#### Running

Entry point (at the moment) for sending the output as an email (agent):

- `notices launch teacher|student --email`

Entry point (at the moment) for updating the "Start Date" and "End Date" fields is:

- `notices launch teacher|student --update_date_fields`

## Moodle side

Create a database activity, and note the name. That name needs to be input into settings.ini file. The activity itself needs to have the following fields:

<img src="http://classroomtechtools.github.io/moodle_daily_notices/fields.png" width="400" />

Note that start date and end date are NOT date fields but instead is a pop-up. The values are populated with the --update_date_fields command (above).

Also note that text in the Attachment field is placed at the bottom of all the notices.

## Output

#### Sample Output

The entires are organized by section:

<img src="http://classroomtechtools.github.io/moodle_daily_notices/notices_sample.png" />

If you define `priority_usernames` in the settings.ini file, those usernames will be given a higher priority and thus appear before all the others.

## Customization or Assistance

Please contact us for further customizations. We can help you install it in a sandbox for your previewing needs. We can customize any of the default behaviour, such as publishing to a WordPress site instead of (or in addition to) email.
