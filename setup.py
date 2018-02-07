# -*- coding: utf-8 -*-
"""Installer for the collective.restapi.pam package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='collective.restapi.pam',
    version='2.0.0.dev0',
    description="An add-on providing plone.restapi endpoint for translations handled using plone.app.multilingual",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='Mikel Larreategi',
    author_email='mlarreategi@codesyntax.com',
    url='https://pypi.python.org/pypi/collective.restapi.pam',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.restapi'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.multilingualbehavior',
        'archetypes.multilingual <2',
        'plone.restapi',
        'plone.app.dexterity',
        'plone.app.multilingual <=2.99',
        'Plone <= 4.99',
    ],
    extras_require={
        'test': [
            'collective.MockMailHost',
            'freezegun',
            'plone.api',
            'plone.app.testing [robot] >= 4.2.2',
            'plone.testing',
            'plone.app.contenttypes <1.2',
            'plone.app.robotframework[debug]',
            'requests',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
