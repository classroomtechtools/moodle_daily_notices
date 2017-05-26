from distutils.core import setup
setup(
    name = "Daily Notices for Moodle",
    packages = ['cli', 'notices', 'gns'],
    version = "1.0",
    description = "",
    author = "Adam Morris",
    author_email = "classroomtechtools.ctt@gmail.com",
    keywords = ["moodle"],
    install_requires = ['click', 'sqlalchemy', 'psycopg2'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        ],
    entry_points='''
        [console_scripts]
        notices=cli.main:notices
    ''',
    long_description = """\
TODO: DESCRIBE THIS!

This version requires Python 3 or later.
"""
)
