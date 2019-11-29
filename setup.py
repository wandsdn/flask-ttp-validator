from setuptools import setup

setup(
    name='flask-ttp-validator',
    version='1.0',
    long_description=__doc__,
    packages=['flask_ttp_validator'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask-Limiter',
        'ttp-tools'
        ]
)
