=============
pytest-zigzag
=============

.. image:: https://travis-ci.org/rcbops/pytest-zigzag.svg?branch=master
    :target: https://travis-ci.org/rcbops/pytest-zigzag
    :alt: See Build Status on Travis CI

Extend py.test for RPC OpenStack testing.

Quick Start Guide
-----------------

1. You can install "pytest-zigzag" via `pip`_ from `PyPI`_ ::

    $ pip install pytest-zigzag

2. Or you can install "pytest-zigzag" via `pip`_ from disk (assumes you're in the root of the repo)::

    $ pip install -e .

Usage
-----

Once installed the plug-in will automatically be loaded by all ``py.test`` test runs executed in the Python environment
in which the ``pytest-zigzag`` was installed.

Features
--------

JUnitXML RPC Specific Properties
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a user executes ``py.test`` tests with the ``--junitxml`` and with this plug-in installed, the resulting XML log file
will contain a test suite properties element. The properties element will contain information gathered about the test
run fetched from the local environment.

Configuration
^^^^^^^^^^^^^

You can supply a json config to this plugin containing a dictionary. Each key / value will become a property name and
value on the test suite node of the resulting xml. There is one required config: pytest_zigzag_env_vars.
This should be a json object where the keys are the environment variable names to be collected, if you set
value to a string that value will be used.  If the value is null it will be pulled from the environment.

The location of the config file can be specified in two ways:

1. In a pytest ini file::

    [pytest]
    pytest-zigzag-config=/path/to/config/file

2. Explicitly on the command line::

    pytest /path/to/test_test.py --pytest-zigzag-config=/path/to/config/file

Any property defined in the config file can be overriden by creating an environment variable of the same name. see this `config_property_overrides.md`_

Contributing
------------

See `CONTRIBUTING.rst`_ for more details on developing for the "pytest-zigzag" project.

Release Process
---------------

See `release_process.rst`_ for information on the release process for 'pytest-zigzag'

Credits
-------

This `Pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `Cookiecutter-pytest-plugin`_ template.

.. _CONTRIBUTING.rst: CONTRIBUTING.rst
.. _release_process.rst: docs/release_process.rst
.. _config_property_overrides.md: docs/config_property_overrides.md
.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi
