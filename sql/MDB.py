from db import DBSession
from db import MoodleDB    # yes, import the module itself, used for getattr statements
from db.MoodleDB import *  # and, yes, import all the terms we need to refer to the tables as classes
from sqlalchemy import and_, not_, or_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import desc, asc
from settings import config_get_section_attribute
from utils import time_now
from sqlalchemy import func, case, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import aliased
from collections import defaultdict
from sqlalchemy.sql.expression import cast, delete

import logging
import re

class MoodleDBSess:
    """
    Implements lower-level convenience methods that handles sessions, transactions, queries
    Errors are not trapped, should be handled at higher level
    """
    def __init__(self):
        self.logger = logging.getLogger('MoodleDBSess')
        self.default_logger = self.logger.info
        self.DBSession = DBSession
        self.and_ = and_

    def table_string_to_class(self, table):
        """
        This provides the whole class with an API whereby
        table_name can be a string that equals the equiv in the actual database
        so that places outside of me don't have to do a bunch of imports
        TODO: Find the native sqlalchemy way of doing this conversion
        @table should be a string
        @returns Database class that can be used in queries
        """
        if table.lower().endswith('data'):
            table = table[:-4] + 'datum'
        if table.endswith('s'):
            table = table[:-1]
        ret = getattr(MoodleDB, table.replace('_', ' ').title().replace(' ', ''))
        return ret

    def wrap_no_result(self, f, *args, **kwargs):
        """
        For simple work, returns None if NoResultFound is encountered
        Most useful when calling an sqlalchemy function like one() and you want
        a simple way to handle an error
        """
        try:
            return f(*args, **kwargs)
        except NoResultFound:
            return None

    def insert_table(self, table, **kwargs):
        with DBSession() as session:
            table_class = self.table_string_to_class(table)
            instance = table_class()
            for key in kwargs.keys():
                setattr(instance, key, kwargs[key])

            session.add(instance)

    def delete_table(self, table, **kwargs):
        with DBSession() as session:
            table_class = self.table_string_to_class(table)
            table_class.delete(**kwargs)

    def get_rows_in_table(self, table, **kwargs):
        """
        @table string of the table name (without the prefix)
        @param kwargs is the where statement
        """
        table_class = self.table_string_to_class(table)
        with DBSession() as session:
            statement = session.query(table_class).filter_by(**kwargs)
        return statement.all()

    def update_table(self, table, where={}, **kwargs):
        """
        Can only update one row...
        """
        table_class = self.table_string_to_class(table)
        with DBSession() as session:
            try:
                instance = session.query(table_class).filter_by(**where).one()
            except MultipleResultsFound:
                self.logger.critical("Cannot update {} with this idnumber: {} because multiple results found".format(table_class, where))
                return
            for key in kwargs.keys():
                setattr(instance, key, kwargs[key])
            session.add(instance)

    def get_user_from_idnumber(self, idnumber):
        with DBSession() as session:
            try:
                ret = session.query(User).filter(User.idnumber == idnumber).one()
            except MultipleResultsFound:
                self.logger.critical("More than one user with this idnumber: {}".format(idnumber))
                ret = None
            except NoResultFound:
                ret = None
        return ret

    def get_course_from_idnumber(self, idnumber):
        with DBSession() as session:
            try:
                ret = session.query(Course).filter(Course.shortname == idnumber).one()
            except MultipleResultsFound:
                self.logger.critical("More than one course with this idnumber: {}".format(idnumber))
                ret = None
            except NoResultFound:
                ret = None
        return ret

    def get_user_from_username(self, username):
        with DBSession() as session:
            ret = session.query(User).filter(User.username == username).one()
        return ret

    def set_user_idnumber_from_username(self, username, idnumber):
        with DBSession() as session:
            ret = session.query(User).filter(User.username == username).one()
            ret.idnumber = idnumber

    def get_column_from_row(self, table, column, **kwargs):
        table_class = self.table_string_to_class(table)
        with DBSession() as session:
            try:
                result = session.query(table_class).filter_by(**kwargs).one()
            except NoResultFound:
                result = None
        if not result:
            return None
        return getattr(result, column)

    def get_list_of_attributes(self, table, attr):
        """
        """
        table_class = self.table_string_to_class(table)
        with DBSession() as session:
            instance = session.query(table_class)
        return [getattr(obj, attr) for obj in instance.all()]

    def parse_user(self, user):
        if isinstance(user, str):
            # passed an idnumber, so let's get the object
            return self.get_user_from_idnumber(user)
        return user

    def get_online_portfolios(self):
        with DBSession() as session:
            statement = session.query(Course).filter(Course.idnumber.startswith('OLP:'))

        for row in statement.all():
            yield re.sub(r'^OLP:', '', row.idnumber)


    def get_user_custom_profile_field(self, user, field_name):
        """
        @param user can be an object or just the idnumber
        @return the value of the custom profile object
        """
        user = self.parse_user(user)
        with DBSession() as session:
            statement = session.query(UserInfoDatum).\
                join(UserInfoField, UserInfoField.id == UserInfoDatum.fieldid).\
                    filter(and_(
                        UserInfoField.shortname == field_name,
                        UserInfoDatum.userid == user.id
                        )
                    )
            try:
                ret = statement.one()
            except MultipleResultsFound:
                self.logger.warning("Multiple fields for {0.username} and {1}; using first() ".format(user, field_name))
                ret = statement.first()
        return ret

class MoodleDBSession(MoodleDBSess):
    """
    High-level convenience routines that handles sessions, transactions, queries
    The difference between high-level and low-level may be up to this programmer's imagination :)
    But basically, anything obviously 'dragonnet-y' is here
    """
    SYSTEM_CONTEXT = 1
    MRBS_EDITOR_ROLE = 10
    TEACHING_LEARNING_CATEGORY_ID = config_get_section_attribute('MOODLE', 'tl_cat_id')

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)


if __name__ == "__main__":

    m = MoodleDBSession()

    # for item in m.get_custom_profile_records():
    #     print(item)

    # result = m.wrap_no_result(m.get_user_from_idnumber, 'xxxx')
    # assert(result is None)

    #for item in m.users_enrolled_in_these_cohorts(['studentsALL']):
    #    print(item.idnumber)
    #for item in m.bell_schedule():
    #    course, student_num, teacher_name, role, group_id, group_name = item

    # for item in m.bell_schedule():
    #     print(item)

    # assert( m.parse_user('38110') in list(m.mrbs_editors()) )
    # assert(m.get_user_schoolid('38110') == '112')

    count = 0
    for user in m.get_mrbs_editors():
        ra_class = m.table_string_to_class('role_assignments')
        if not ('@ssis-suzhou' in user.email):
            with DBSession() as session:
                which = session.query(ra_class).filter_by(contextid=m.SYSTEM_CONTEXT,roleid=m.MRBS_EDITOR_ROLE,userid=user.id).one()
                #session.delete(which)
            print('deleted: {} component: <{}>'.format(user.username, which.component))
            count = count + 1

    print("total: {}".format(count))
    # for student, parent in m.get_parent_student_links():
    #     print(student)
    #     print(parent)
    #     print()

    # for item in m.get_timetable_data():
    #     input(item)


    # for item in m.get_course_metadata():
    #     print(item)
    #     input()


    # m.add_cohort('blahblahALL', 'All Parents')


    # for item in m.get_online_portfolios():
    #     print(item)

