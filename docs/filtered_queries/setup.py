from setuptools import setup

requires = [
    'pyramid',
    'pyramid_tm',
    'pyramid_jinja2',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'psycopg2',
    'waitress',
    'nose',
    'webtest'
]
setup(name='mysite',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = mysite:main
      [console_scripts]
      initialize_db = mysite.scripts.initialize_db:main
      """
      )
