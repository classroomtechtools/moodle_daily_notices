from sql import MoodleDBSession
from mod.database import RelativeDateFieldUpdater
from utils.Dates import today, tomorrow, yesterday, day_after_tomorrow, timestamp_to_python_date
import datetime
import re, json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            encoded_object = datetime.datetime.strftime(obj, '%b %d, %Y')
        else:
            return json.JSONEncoder.default(self, obj)
        return encoded_object

class NoticesRelativeDateFieldUpdater(RelativeDateFieldUpdater):
    pass

class StartDateField(NoticesRelativeDateFieldUpdater):
    def first(self):
        return day_after_tomorrow()

class EndDateField(NoticesRelativeDateFieldUpdater):
    def first(self):
        return day_after_tomorrow()

class DatabaseObject:
    """
    Represents an item in the database
    """
    def __init__(self, **kwargs):
        if kwargs:
            self.define(**kwargs)
        self._months = {}
        for month in range(1, 13):
            month_str = datetime.date(2012, month, 1).strftime('%b').lower()
            self._months[month_str] = month

    def __repr__(self):
        return "\n     ".join(['{}: {}'.format(key, self.__dict__[key]) for key in self.__dict__.keys()])

    def define(self, *args, **kwargs):
        if args:
            if len(args) == 2:
                setattr(self, args[0].replace(' ', '_').lower(), args[1])
        for field in kwargs.keys():
            setattr(self, field.replace(' ', '_').lower(), kwargs[field])

    def time_created_within_start_end(self, start, end):
        """
        Returns boolean whether timecreated falls within start and end
        Converts start and end to datetime objects if needed, and when it does so
        it uses the extreme boundaries (start time is midnight, end time is one second before midnight)
        """
        if isinstance(start, datetime.date):
            start = datetime.datetime.combine(start, datetime.time())
        if isinstance(end, datetime.date):
            end = datetime.datetime.combine(end, datetime.time(hour=23, minute=59, second=59))
        return self.time_created >= start and self.time_created <= end

    def time_modified_within_start_end(self, start, end):
        """
        Returns boolean whether timecreated falls within start and end
        Converts start and end to datetime objects if needed, and when it does so
        it uses the extreme boundaries (start time is midnight, end time is one second before midnight)
        """
        if isinstance(start, datetime.date):
            start = datetime.datetime.combine(start, datetime.time())
        if isinstance(end, datetime.date):
            end = datetime.datetime.combine(end, datetime.time(hour=23, minute=59, second=59))
        return self.time_modified >= start and self.time_created <= end

    def date_objects(self):
        """
        Returns the startdate and enddate as a datetime objects
        None means we don't have them
        Processing only happens once, results are stored as private internal objects
        You can reset it if you need to by setting _date_objects to None
        """
        if hasattr(self, '_date_objects') and not self._date_objects == None:
            return self._date_objects
        
        if not hasattr(self, 'start_date') or not hasattr(self, 'end_date'):
            return (None, None)

        if not self.start_date:
            return (None, None)

        date_objects = []   # Dates to compare to, needed because strings need to be converted into datetime objects

        for this_date in (re.search(r'\((.*)\)$',
                                    self.start_date).group(1),
                                    re.search(r'\((.*)\)$', self.end_date).group(1) if self.end_date else None):
            if not this_date:
                date_objects.append( None )
            else:
                split = this_date.split(' ')
                try:
                    remove_non_digits = lambda x: int(re.sub(r'[^0-9]', '', x))
                    this_day   = remove_non_digits(split[0])
                except ValueError:
                    return (None, None)
                try:
                    this_month = self._months.get(split[1].lower())
                except ValueError:
                    return (None, None)
                if not this_month:
                    return (None, None)
                try:
                    this_year = int(split[2])
                except (IndexError, ValueError):
                    this_year  = today().year - 1
                date_objects.append( datetime.date(this_year, this_month, this_day) )

        if not date_objects:
            date_objects = (None, None)
        self._date_objects = date_objects   # stores this for later so we don't have to process it all over again
        return self._date_objects

    def date_within(self, to_compare_date):
        """
        Given a datetime object date, determines if this object matches the date expected,
        that is, the date of this object falls within the passed date
        Comparison using datetime objects is done, conversion needed
        """
        start_compare, end_compare = self.date_objects()
        # Get the obvious cases done first
        if not start_compare:
            return False        
        # If end_compare is not defined, then we assume it's for one day only, and therefore end_compare should equal start_compare
        if not end_compare:
            end_compare = start_compare

        # Do the actual comparison
        return to_compare_date >= start_compare and to_compare_date <= end_compare

    def determine_section(self, field, default_value=None):
        """
        Processes a database item and assigns it a section
        """
        # Important to convert to compatible version
        field = field.replace(' ', '_').lower()
        if hasattr(self, field):
            self.section = getattr(self, field)
        else:
            self.section = default_value

    def determine_priority(self, the_date, priority_id_list):
        """
        Puts any user who prioritized number starts at 1
        If not any priority user, starts at value of 10
        Then, calculates priority based on how far away we are from having been published
        """
        user_id = self.user_id
        first_published, _ = self.date_objects()
        if user_id in priority_id_list:
            priority = 1    # one digit for highest priority
        else:
            priority = 10   # two digits for lower priority

        days_since = (datetime.date(the_date.year, the_date.month, the_date.day) - first_published).days   # substraction of two datetime object results in datetime object, which has 'days'
        if days_since < 0:
            raise NotImplmented('Huh? This was first published sometime in the future? Should not happen!')
        priority += days_since * 100
        self.priority = priority

    def __str__(self):
        return ", ".join( ["{}: {}".format(key, self.__dict__[key]) for key in self.__dict__ if self.__dict__[key] and not key.startswith('_') ] )

    @property
    def output_data(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

class DatabaseObjects(MoodleDBSession):
    """
    Defines the objects for use by the application
    """
    def __init__(self, database_name=None):
        """
        database_name is the database we are using
        If defined, it will use custom sql to get the information we need, and then put it into objects the application can use
        If not defined, then you're making a blank object, which might be useful to you

        Sets up the model accordingly. The sql is in the same place as the code that unpacks the sql
        and puts the resulting infomation into python objects. This is a good way to do it.
        """
        super().__init__()
        self.database_name = database_name
        self._db = []
        if not self.database_name:
            return

        self.database_id = self.get_column_from_row('data', 'id', name=self.database_name)

        # First get the information, samples if that's what is wanted
        # TODO: Verify database_name
        # The following sql gets a "flat" list of items:
        # (recordid, firstname, lastname, institution, field, content)
        # where each row's field has content are unique but the others all repeat for the same recordid
        # Since it's "flat", we then have to unpack to put all the items with the same recordid into the same object
        # I choose to do that with python below rather than the sql itself, which is possible (this is known as making a pivot table)
        # But doing it in python is better because we don't have to worry about whether it's mysql or postgres or what

        DataRecords = self.table_string_to_class('data_records')
        DataFields = self.table_string_to_class('data_fields')
        DataContent = self.table_string_to_class('data_content')
        User = self.table_string_to_class('user')

        with self.DBSession() as session:

            statement = session.query(DataContent.recordid, User.id, User.firstname, User.lastname, User.institution, 
                DataRecords.timecreated, DataRecords.timemodified, DataFields.name, DataContent.content).\
                select_from(DataContent).\
                    join(DataRecords, self.and_(
                        DataRecords.id == DataContent.recordid,
                        DataRecords.dataid == self.database_id
                        )
                    ).\
                    join(User, User.id == DataRecords.userid).\
                    join(DataFields, DataFields.id == DataContent.fieldid)

            sql_result = statement.all()

        # Unpack the sql results into useable objects.
        # NOTE: This essentially converts multiple rows into a pivot table

        # SET UP THE dbid FIELD THAT IMPLEMENTS COOL EDIT BUTTON NEXT TO ITEM
        with self.DBSession() as session:
            statement = session.query(DataFields).filter_by(name='dbid', dataid=self.database_id)
            self.dbid_id = statement.one().id

        unique_records = []
        for row in sql_result:
            recordid = row[0]
            if not recordid in unique_records:
                unique_records.append( recordid )
        # Now go through each unique record
        for unique_record in unique_records:
            # Get all records with single unique ID
            records = [row for row in sql_result if row[0] == unique_record]
            if not records or len(records) == 0:
                continue
            # Put the shared info into one place for convenience
            shared_info = records[0][:7]
            # Got the records with a single unique ID, now pack them in
            new_object = DatabaseObject()
            new_object.define(record_id = shared_info[0])
            new_object.define(user_id = shared_info[1])
            new_object.define(user_first_name = shared_info[2])
            new_object.define(user_last_name = shared_info[3])
            new_object.define(user_preferred = shared_info[4])
            new_object.define(time_created = timestamp_to_python_date(shared_info[5]))
            new_object.define(time_modified = timestamp_to_python_date(shared_info[6]))
            if new_object.user_preferred:
                new_object.user = new_object.user_preferred
            else:
                new_object.user = "{} {}".format(new_object.user_first_name, new_object.user_last_name)
            for row in records:
                # Put non-unique information in one by one
                field = row[7]
                value = row[8]
                new_object.define(field, value)

            # Okay, we got everything, so now place it into our internal object
            if hasattr(new_object, 'dbid') and not new_object.dbid:
                self.update_table('data_content', where=dict(
                        recordid=new_object.record_id,
                        fieldid=self.dbid_id
                    ), 
                    content=new_object.record_id)

                new_object.dbid = recordid

            self.add(new_object)
            
    def add(self, obj):
        #print(json.dumps(obj.output_data, cls=DateTimeEncoder, indent=4))
        self._db.append(obj)

    def items_within_date(self, date):
        return (item for item in self._db if item.date_within(date))

    def time_created_happened_between(self, start, end):
        return (item for item in self._db if item.time_created_within_start_end(start, end))

    def sort(self, lst):
        try:
            lst.sort(key = lambda x: x.priority)
        except AttributeError:
            pass
        return lst

    def get_items_by_section(self, section):
        result = [item for item in self if hasattr(item, 'section') and item.section == section]
        return self.sort(result)

    def get_all_items(self):
        return self.sort(self._db)

    def all_values_for_field(self, field):
        values = []
        for item in self:
            if hasattr(item, field):
                value = getattr(item, field)
                if not value in values:
                    values.append(value)
        return values
    
    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        which = self._iter_index
        self._iter_index += 1
        if which >= len(self._db):
            raise StopIteration
        return self._db[which]

    def __str__(self):
        return "\n/---- Database Objects ----\n" + "\n".join(["| {}".format(str(item)) for item in self]) + "\n\--------------------------\n"

class SampleDatabaseObjects(DatabaseObjects):
    pass
