#!/usr/bin/env python

from setuptools import setup

setup(
    # GETTING-STARTED: set your app name:
    name='YourAppName',
    # GETTING-STARTED: set your app version:
    version='1.0',
    # GETTING-STARTED: set your app description:
    description='OpenShift App',
    # GETTING-STARTED: set author name (your name):
    author='Your Name',
    # GETTING-STARTED: set author email (your email):
    author_email='example@example.com',
    # GETTING-STARTED: set author url (your url):
    url='http://www.python.org/sigs/distutils-sig/',
    # GETTING-STARTED: define required django version:
    install_requires=[
        'Django==1.8.4',
        # 'django-filter==0.12.0',
        # 'djangorestframework==3.3.2',
        # 'et-xmlfile==1.0.1',
        # 'jdcal==1.2',
        # 'Markdown==2.6.5',
        # 'mysqlclient==1.3.7',
        'django-rq==0.9.0',
        # 'numpy==1.11.0',
        # 'openpyxl',
        # 'scikit-learn==0.17.1',
        # 'scipy==0.17.0'
    ],
    dependency_links=[
        'https://pypi.python.org/simple/django/'
    ],
)
