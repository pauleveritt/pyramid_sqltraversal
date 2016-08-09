from setuptools import setup

requires = [
    'pyramid',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'nose',
    'webtest',
    'psycopg2',
    'sphinx'
]
setup(name='pyramid_sqltraversal',
      install_requires=requires
      )
