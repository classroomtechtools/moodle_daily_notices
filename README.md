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

You should then see output indicating that the software has been installed into the virtualenv. 

##### Upgrading

If improvements are made then you may wish to update the software:

- cd /path/to/moodle_daily_notices
- git pull origin master
- pip install -e .

#### Setup

You need to have a settings.ini file with the appropriate content.

- cp settings_default.ini settings.ini
- nano settings_default.ini
- (edit the file according to your needs)

There is a place for student and teacher notices, but you could have just one if desired. The "db_activity" attributes have to coorespond to the database activity created on the Moodle side.

#### Running

Entry point (at the moment) for outputing the emails is, this will not work unless Moodle side is also set up (below):

- notices launch teacher|student --email

Entry point (at the moment) for updating the "Start Date" and "End Date" fields is:

- notices launch teacher|student --update_date_fields

## Moodle side

Create a database activity, and note the name. That name needs to be input into settings.ini file. The activity itself needs to have the following fields:

<img src="http://classroomtechtools.github.io/moodle_daily_notices/fields.png" width="400" />

Note that start date and end date are NOT date fields but instead is a pop-up. The values are populated with the --update_date_fields command (above).

## Sample Output

This is an sample output.

<img src="http://classroomtechtools.github.io/moodle_daily_notices/notices_sample.png" />

While the default behaviour can be emailed to a group, it is also possible to publish it to a WordPress site or multi-site.

## Customization or Assistance

Please contact us for further customizations. We can help you install it in a sandbox for your previewing needs.
