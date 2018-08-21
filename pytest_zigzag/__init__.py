# -*- coding: utf-8 -*-

__version__ = '0.0.0'

# ======================================================================================================================
# Imports
# ======================================================================================================================
import os
import pytest
import pkg_resources
from datetime import datetime


# ======================================================================================================================
# Globals
# ======================================================================================================================
TEST_STEPS_MARK = 'test_case_with_steps'
ASC_ENV_VARS = ['BUILD_URL',
                'BUILD_NUMBER',
                'RE_JOB_ACTION',
                'RE_JOB_IMAGE',
                'RE_JOB_SCENARIO',
                'RE_JOB_BRANCH',
                'ZIGZAG_RELEASE',
                'ZIGZAG_PRODUCT_RELEASE',
                'OS_ARTIFACT_SHA',
                'PYTHON_ARTIFACT_SHA',
                'APT_ARTIFACT_SHA',
                'REPO_URL',
                'JOB_NAME',
                'MOLECULE_TEST_REPO',
                'MOLECULE_SCENARIO_NAME',
                'MOLECULE_GIT_COMMIT']
MK8S_ENV_VARS = ['BUILD_URL',
                 'BUILD_NUMBER',
                 'BUILD_ID',
                 'NODE_NAME',
                 'JOB_NAME',
                 'BUILD_TAG',
                 'JENKINS_URL',
                 'EXECUTOR_NUMBER',
                 'WORKSPACE',
                 'CVS_BRANCH',
                 'GIT_COMMIT',
                 'GIT_URL',
                 'GIT_BRANCH',
                 'GIT_LOCAL_BRANCH',
                 'GIT_AUTHOR_NAME',
                 'GIT_AUTHOR_EMAIL',
                 'BRANCH_NAME',
                 'CHANGE_AUTHOR_DISPLAY_NAME',
                 'CHANGE_AUTHOR',
                 'CHANGE_BRANCH',
                 'CHANGE_FORK',
                 'CHANGE_ID',
                 'CHANGE_TARGET',
                 'CHANGE_TITLE',
                 'CHANGE_URL',
                 'JOB_URL',
                 'NODE_LABELS',
                 'NODE_NAME',
                 'PWD',
                 'STAGE_NAME']


# ======================================================================================================================
# Functions: Private
# ======================================================================================================================
def _capture_marks(items, marks):
    """Add XML properties group to each 'testcase' element that captures the specified marks.

    Args:
        items (list(_pytest.nodes.Item)): List of item objects.
        marks (list(str)): A list of marks to capture and record in JUnitXML for each 'testcase'.
    """

    for item in items:
        # If item is in a class then check to see if this item is a test step or test case.
        item.user_properties.append(('test_step', 'true' if item.get_marker(TEST_STEPS_MARK) else 'false'))
        for marker in [item.get_marker(mark) for mark in marks if item.get_marker(mark)]:
            for arg in marker.args:
                item.user_properties.append((marker.name, arg))


def _get_ci_environment(session):
    """Gets the ci-environment used when executing tests
    default is 'asc'

    Args:
        session (_pytest.main.Session): The pytest session object

    Returns:
        str: The value of the config with the highest precedence
    """

    #  Try to get configs from CLI and ini
    try:
        cli_option = session.config.getoption('--ci-environment')
    except ValueError:
        cli_option = None
    try:
        ini_option = session.config.getini('ci-environment')
    except ValueError:
        ini_option = None

    # Determine if the option passed with the highest precedence is a valid option
    highest_precedence = cli_option or ini_option or 'asc'
    white_list = ['asc', 'mk8s']
    if not any(x == highest_precedence for x in white_list):
        raise RuntimeError(
            "The value {} is not a valid value for the 'ci-environment' configuration".format(highest_precedence))

    return highest_precedence


# ======================================================================================================================
# Hooks
# ======================================================================================================================
@pytest.hookimpl(tryfirst=True)
def pytest_runtestloop(session):
    """Add XML properties group to the 'testsuite' element that captures the values for specified environment variables.

    Args:
        session (_pytest.main.Session): The pytest session object
    """

    if session.config.pluginmanager.hasplugin('junitxml'):
            junit_xml_config = getattr(session.config, '_xml', None)

            if junit_xml_config:
                ci_environment = _get_ci_environment(session)
                junit_xml_config.add_global_property('ci-environment', ci_environment)
                if ci_environment == 'asc':
                    for env_var in ASC_ENV_VARS:
                        junit_xml_config.add_global_property(env_var, os.getenv(env_var, 'Unknown'))
                elif ci_environment == 'mk8s':
                    for env_var in MK8S_ENV_VARS:
                        junit_xml_config.add_global_property(env_var, os.getenv(env_var, 'Unknown'))


def pytest_collection_modifyitems(items):
    """Called after collection has been performed, may filter or re-order the items in-place.

    Args:
        items (list(_pytest.nodes.Item)): List of item objects.
    """

    _capture_marks(items, ('test_id', 'jira'))


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Add XML properties group to the 'testcase' element that captures start time in UTC. Also, skip test cases
    in a class where the previous test case failed.

    Args:
        item (_pytest.nodes.Item): An item object.
    """

    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    item.user_properties.append(('start_time', now))

    if "test_case_with_steps" in item.keywords and ('teardown' not in item.name or 'setup' not in item.name):
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.skip("because previous test failed: {}".format(previousfailed.name))


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item):
    """Add XML properties group to the 'testcase' element that captures start time in UTC.

    Args:
        item (_pytest.nodes.Item): An item object.
    """

    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    item.user_properties.append(('end_time', now))


def pytest_addoption(parser):
    """Adds a config option to pytest

    Args:
        parser (_pytest.config.Parser): A parser object
    """

    config_option = "ci-environment"
    config_option_help = "The ci-environment used to execute the tests, (default: 'asc')"
    parser.addini(config_option, config_option_help)
    parser.addoption("--{}".format(config_option), help=config_option_help)


def pytest_runtest_makereport(item, call):
    """Re-write the report concerning test cases with steps so it looks correct.

    Args:
        item (_pytest.nodes.Item): An item object.
        call (_pytest.runner.CallInfo): A call info object.
    """

    if "test_case_with_steps" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


# ======================================================================================================================
# Functions: Public
# ======================================================================================================================
def get_xsd(ci_environment='asc'):
    """Retrieve a XSD for validating JUnitXML results produced by this plug-in.

    Args:
        ci_environment (str): the value found in the ci-environment global property from the XML

    Returns:
        io.BytesIO: A file like stream object.
    """

    if ci_environment == 'asc':
        return pkg_resources.resource_stream('pytest_zigzag', 'data/molecule_junit.xsd')
    elif ci_environment == 'mk8s':
        return pkg_resources.resource_stream('pytest_zigzag', 'data/mk8s_junit.xsd')
    else:
        raise RuntimeError("Unknown ci-environment '{}'".format(ci_environment))
