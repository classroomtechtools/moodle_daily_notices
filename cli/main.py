import click

class Object:
    def __init__(self):
        pass
        
    # define common methods here

#
# Define global options here
#
@click.group()
@click.pass_context
def main(ctx):
    # Doesn't do much now, but leave it as boilerplate for when there are global flags n such
    ctx.obj = Object()


@main.group()
@click.argument('which', metavar="<student> or <teacher>")
@click.option('--date_offset', default='1', help="1 for tomorrow, -1 for yesterday; default=1", metavar='<INT>')
@click.option('--_date', help="Useful for debugging; today if not passed", metavar="<Dec 10 2015>")
@click.pass_obj
def notices(obj, which, _date=None, date_offset=None):
    """
    Manage and launch the Student and Teacher notices stuff
    """
    obj.student_notices = 'student' in which
    obj.teacher_notices = 'teacher' in which

    # first calc and setup _date stuff
    import time, datetime
    if _date:
        # If we are explicitely passed date, then use that
        time_object = time.strptime(_date, "%b %d %Y")
        date_object = datetime.date(
            month=time_object.tm_mon,
            day=time_object.tm_mday,
            year=time_object.tm_year
            )
    else:
        # Calculate the date we need by date_offset
        date_object = datetime.date.today() + datetime.timedelta(days=int(date_offset))

    if obj.student_notices:
        from notices.StudentNotices import Student_Notices
        obj.notices = Student_Notices(date_object)
    elif obj.teacher_notices:
        from notices.TeacherNotices import Teacher_Notices
        obj.notices = Teacher_Notices(date_object)
    else:
        click.echo('Bad Argument: Pass me either "teacher" or "student"')
        exit()

@notices.command()
@click.pass_obj
def output(obj):
    obj.notices.print_email([])

@notices.command()
@click.option('--email/--no_email', default=False, help="Email them or not (requires smtp server of course)")
@click.option('--edit_email/--no_edit_email', default=False, help="Email to some agent an email with edit links")
@click.option('--output/--no_output', default=False, help="Output to stdout?")
@click.option('--publish/--dont_publish', default=False, help="Goes to group-sec-all and elem-sec-all")
@click.option('--update_date_fields/--dont_update_date_fields', default=False, help="Output to stdout?")
@click.pass_obj
def launch(obj, email=False, edit_email=False, output=False, publish=False, update_date_fields=False):
    """
    Runs the student notices
    """
     
    if email:
        if publish:
            obj.notices.email_editing = False
            obj.notices.agent_map = {
                'email@example.com':['Whole School', 'Secondary', 'Elementary'],
                'email@example.com':['Whole School', 'Elementary', 'Secondary']
                }

        obj.notices.email_to_agents()

    if edit_email:
        obj.notices.email_editing = True
        obj.notices.email_to_agents()

    if output:
        obj.notices.print_email([])

    if update_date_fields:
        obj.notices.update_date_fields()


@notices.command()
@click.option('--url', default=None, help="The URL for the WordPress site; default is to use settings.ini")
@click.option('--multisite/--not_multisite', default=True, help="Is the WP blog multisite or not?")
@click.option('--blog', default=None, help="If --multisite, then requires blog param")
@click.option('--author', default=None, help="Username of the author to use")
@click.option('--hour', default='immediately', help="Schedule the blog post this way", metavar='<H:M>')
@click.pass_obj
def post_to_wordpress(obj, url=None, multisite=True, blog=None, author=None, hour='immediately'):
    if multisite and not blog:
        click.secho('Multisite requires the blog parameter')
        exit()

    if hour == 'immediately':
        click.secho('Must have an hour argument', fg='red') #TODO
        exit()
    else:
        import time
        when = time.strptime(hour, '%H:%M')

    if not author:
        click.secho('Must send author argument', fg='red')
        exit()

    obj.notices.post_to_wordpress(url, blog, author, when)



