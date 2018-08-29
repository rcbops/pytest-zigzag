# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import os
import pytest
from datetime import datetime
# noinspection PyPackageRequirements
from zigzag.zigzag import ZigZag
from pytest_zigzag.session_messages import SessionMessages

__version__ = '0.1.0'

# ======================================================================================================================
# Globals
# ======================================================================================================================
SESSION_MESSAGES = SessionMessages()
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

    # Determine if the option passed with the highest precedence is a valid option
    highest_precedence = _get_option_of_highest_precedence(session, 'ci-environment') or 'asc'
    white_list = ['asc', 'mk8s']
    if not any(x == highest_precedence for x in white_list):
        raise RuntimeError(
            "The value {} is not a valid value for the 'ci-environment' configuration".format(highest_precedence))

    return highest_precedence


def _get_option_of_highest_precedence(session, option_name):
    """looks in the session and returns the option of the highest precedence
    This assumes that there are options and flags that are equivalent

    Args:
        session (_pytest.main.Session): The pytest session object
        option_name (str): The name of the option

    Returns:
        str: The value of the option that is of highest precedence
        None: no value is present
    """
    #  Try to get configs from CLI and ini
    try:
        cli_option = session.config.getoption("--{}".format(option_name))
    except ValueError:
        cli_option = None
    try:
        ini_option = session.config.getini(option_name)
    except ValueError:
        ini_option = None
    highest_precedence = cli_option or ini_option
    return highest_precedence


# ======================================================================================================================
# Hooks
# ======================================================================================================================
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    """This hook is used by pytest to build the junit XML
    Using ZigZag as a library we upload in the pytest runtime

    Args:
        session (_pytest.main.Session): The pytest session object
    """
    SESSION_MESSAGES.drain()  # need to reset this on every pass through this hook
    if session.config.pluginmanager.hasplugin('junitxml'):
        zz_option = _get_option_of_highest_precedence(session, 'zigzag')
        if zz_option:
            qtest_project_id = _get_option_of_highest_precedence(session, 'qtest-project-id')
            try:
                junit_file_path = getattr(session.config, '_xml', None).logfile
                if not qtest_project_id:
                    raise RuntimeError("'qtest-project-id' is required when using ZigZag")
                zz = ZigZag(junit_file_path, os.environ['QTEST_API_TOKEN'], qtest_project_id, None)
                job_id = zz.upload_test_results()
                SESSION_MESSAGES.append("ZigZag upload was successful!")
                SESSION_MESSAGES.append("Queue Job ID: {}".format(job_id))
            except Exception as e:  # we want this super broad so we dont break test execution
                SESSION_MESSAGES.append('The ZigZag upload was not successful')
                SESSION_MESSAGES.append("Original error message:\n\n{}".format(str(e)))


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter):
    """Use this hook to add what we did to the terminal report"""
    for message in SESSION_MESSAGES:
        terminalreporter.write_line(message)


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

    # options related to publishing
    zigzag_help = 'Enable automatic publishing of test results using ZigZag'
    parser.addini('zigzag', zigzag_help, type='bool', default=False)
    parser.addoption('--zigzag', help=zigzag_help, action="store_true", default=False)

    project_help = 'The target project ID to use as a destination for test results published by ZigZag'
    parser.addini('qtest-project-id', project_help, default=None)
    parser.addoption('--qtest-project-id', help=project_help, default=None)


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
