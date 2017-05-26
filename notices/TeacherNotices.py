from settings import config_get_section_attribute
from .DatabaseBase import ExtendMoodleDatabaseToAutoEmailer
from .Common import *


class Teacher_Notices(ExtendMoodleDatabaseToAutoEmailer):
    """
    Converts a database on moodle into a useable system that emails users
    """

    def post_to_wordpress(self, *args, **kwargs):
        """ Teacher notices doesn't have a wordpress site ...  yet? """
        raise NotImplemented

    def get_subject(self, just_date=False):
        if just_date:
            return self.subject_output[20:]
        else:
            return self.subject_output

    def get_html(self, first_p_block=""):
        d = {
            'first_p_block':first_p_block
            }
        return self.html_output.format(**d)

    def section_not_found(self, tag):
        """ What to do? """
        pass

