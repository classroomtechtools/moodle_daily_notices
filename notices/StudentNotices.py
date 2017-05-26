from settings import config_get_section_attribute
from .DatabaseBase import ExtendMoodleDatabaseToAutoEmailer
from .Common import *


class Student_Notices(ExtendMoodleDatabaseToAutoEmailer):
    """
    Converts a database on moodle into a useable system that emails users
    """

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

    def tag_not_found(self, tag):
        """ What to do? """
        pass


