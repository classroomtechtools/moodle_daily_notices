# Create a globally-available session_maker for the Moodle database
# TODO: Make this more portable
from settings import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

db_username = config['MOODLE'].get('db_username')
db_prefix = config['MOODLE'].get('db_prefix')
db_password = config['MOODLE'].get('db_password')
db_host = config['MOODLE'].get('db_host')
db_name = config['MOODLE'].get('db_name')

engine =  create_engine(
   f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}',
        max_overflow=0, pool_size=100)

session_maker = sessionmaker(
    bind=engine,
    expire_on_commit=False
    )

@contextmanager
def DBSession():
    session = session_maker()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

__all__ = [DBSession]
