from setuptools import setup

setup(
    name='django-secrets-fields',
    version='0.0.1',
    description='Django encrypted model field that fetches the value from multiple sources',
    author='Ryan Shaw',
    author_email='ryan.shaw@min.vc',
    packages=['secrets_fields'],
    install_requires=[
        'boto3'
        'Django>=3',
    ],
)
