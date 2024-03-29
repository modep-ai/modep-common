import sys

from setuptools import find_packages, setup


setup(
    name="modep_common",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        'Flask==2.0.1',
        'Flask-Login==0.5.0',
        'Flask-SQLAlchemy==2.5.1',
        'google-api-core==1.30.0',
        'google-auth==1.30.2',
        'google-cloud-core==1.6.0',
        'google-cloud-storage==1.38.0',
        'google-crc32c==1.1.2',
        'google-resumable-media==1.3.0',
        'googleapis-common-protos==1.53.0',
        'psycopg2-binary==2.8.6',
        'PyYAML==5.4.1',
        'SQLAlchemy==1.4.17',
        'Werkzeug==2.0.1',
    ]
)
