# -*- coding: utf-8 -*-

"""Test cases for the 'pytest_collection_modifyitems' hook function for recording the UUID for test cases."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import os
import pytest
from tests.conftest import run_and_parse_with_config
from dateutil import parser as date_parser


# ======================================================================================================================
# Tests
# ======================================================================================================================
def test_uuid_mark_present(testdir, single_decorated_test_function, simple_test_config):
    """Verify that 'test_id' property element is present when a test is decorated with a UUID mark."""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))

    junit_xml = run_and_parse_with_config(testdir, simple_test_config)[0]

    # Test
    assert junit_xml.get_testcase_properties(test_name_exp)[mark_type_exp] == test_id_exp


def test_jira_mark_present(testdir, single_decorated_test_function, simple_test_config):
    """Verify that 'jira' property element is present when a test is decorated with a Jira mark."""

    # Expect
    mark_type_exp = 'jira'
    jira_id_exp = 'ASC-123'
    test_name_exp = 'test_jira'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=jira_id_exp,
                                                             test_name=test_name_exp))

    junit_xml = run_and_parse_with_config(testdir, simple_test_config)[0]

    # Test
    assert junit_xml.get_testcase_properties(test_name_exp)[mark_type_exp] == jira_id_exp


def test_mark_with_multiple_arguments(testdir, simple_test_config):
    """Verify that multiple property elements are present when a test is decorated with a mark containing multiple
    arguments.
    """

    # Expect
    jira_ids_exp = {'jira_id0': 'ASC-123', 'jira_id1': 'ASC-124'}
    test_name_exp = 'test_jira'

    # Setup
    testdir.makepyfile("""
                import pytest
                @pytest.mark.jira('{jira_id0}', '{jira_id1}')
                def {test_name}():
                    pass
    """.format(test_name=test_name_exp, **jira_ids_exp))

    junit_xml = run_and_parse_with_config(testdir, simple_test_config)[0]

    # Test (Note: So tox and py.test disagree about the ordering of marks, therefore we sort them first.)
    assert sorted(junit_xml.get_testcase_property(test_name_exp, 'jira')) == sorted(jira_ids_exp.values())


def test_multiple_marks(testdir, simple_test_config):
    """Verify that multiple property elements are present when a test is decorated with multiple marks."""

    # Expect
    test_ids_exp = {'test_id0': 'first', 'test_id1': 'second'}
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile("""
                import pytest
                @pytest.mark.test_id('{test_id1}')
                @pytest.mark.test_id('{test_id0}')
                def {test_name}():
                    pass
    """.format(test_name=test_name_exp, **test_ids_exp))

    junit_xml = run_and_parse_with_config(testdir, simple_test_config)[0]

    # Test (Note: So tox and py.test disagree about the ordering of marks, therefore we sort them first.)
    assert sorted(junit_xml.get_testcase_property(test_name_exp, 'test_id')) == sorted(test_ids_exp.values())


def test_multiple_marks_with_multiple_arguments(testdir, simple_test_config):
    """Verify that multiple property elements are present when a test is decorated with multiple marks with each
    containing multiple arguments.
    """

    # Expect
    jira_ids_exp = {'jira_id0': 'ASC-123',
                    'jira_id1': 'ASC-124',
                    'jira_id2': 'ASC-125',
                    'jira_id3': 'ASC-126'}
    test_name_exp = 'test_jira'

    # Setup
    testdir.makepyfile("""
                import pytest
                @pytest.mark.jira('{jira_id2}', '{jira_id3}')
                @pytest.mark.jira('{jira_id0}', '{jira_id1}')
                def {test_name}():
                    pass
    """.format(test_name=test_name_exp, **jira_ids_exp))

    junit_xml = run_and_parse_with_config(testdir, simple_test_config)[0]

    # Test (Note: So tox and py.test disagree about the ordering of marks, therefore we sort them first.)
    assert sorted(junit_xml.get_testcase_property(test_name_exp, 'jira')) == sorted(jira_ids_exp.values())


def test_multiple_test_cases_with_marks_present(testdir, simple_test_config):
    """Verify that 'test_id' and 'jira' property elements are present when multiple tests are decorated with
    required marks.
    """

    # Expect
    test_info = [{'test_name': 'test_mark1',
                  'test_id': 'first',
                  'jira_id': '1st'},
                 {'test_name': 'test_mark2',
                  'test_id': 'second',
                  'jira_id': '2nd'}]

    # Setup
    test_py_file = \
        """
        import pytest
        @pytest.mark.test_id('{test_id}')
        @pytest.mark.jira('{jira_id}')
        def {test_name}():
            pass

        """

    testdir.makepyfile(test_py_file.format(**test_info[0]), test_py_file.format(**test_info[1]))

    junit_xml = run_and_parse_with_config(testdir, simple_test_config)[0]

    # Test
    for info in test_info:
        assert junit_xml.get_testcase_property(info['test_name'], 'test_id') == [info['test_id']]
        assert junit_xml.get_testcase_property(info['test_name'], 'jira') == [info['jira_id']]


def test_missing_marks(testdir, undecorated_test_function, simple_test_config):
    """Verify that 'test_id' and 'jira' property elements are absent when a test is NOT decorated with required
    marks.
    """

    # Expect
    test_name_exp = 'test_no_marks'

    # Setup
    testdir.makepyfile(undecorated_test_function.format(test_name=test_name_exp))

    junit_xml = run_and_parse_with_config(testdir, simple_test_config)[0]

    # Test
    assert 'test_id' not in junit_xml.get_testcase_properties(test_name_exp).keys()
    assert 'jira' not in junit_xml.get_testcase_properties(test_name_exp).keys()


@pytest.mark.skipif('SKIP_LONG_RUNNING_TESTS' in os.environ, reason='Impatient developer is impatient')
def test_start_time(testdir, sleepy_test_function, simple_test_config):
    """Verify that 'start_time' property element is present."""

    # Expect
    test_name_exp = 'test_i_can_has_start_time'

    # Setup
    testdir.makepyfile(sleepy_test_function.format(test_name=test_name_exp, seconds='1'))

    junit_xml = run_and_parse_with_config(testdir, simple_test_config)[0]

    # Test
    assert 'start_time' in junit_xml.get_testcase_properties(test_name_exp).keys()


@pytest.mark.skipif('SKIP_LONG_RUNNING_TESTS' in os.environ, reason='Impatient developer is impatient')
def test_end_time(testdir, sleepy_test_function, simple_test_config):
    """Verify that 'end_time' property element is present."""

    # Expect
    test_name_exp = 'test_i_can_has_end_time'

    # Setup
    testdir.makepyfile(sleepy_test_function.format(test_name=test_name_exp, seconds='1'))

    junit_xml = run_and_parse_with_config(testdir, simple_test_config)[0]

    # Test
    assert 'end_time' in junit_xml.get_testcase_properties(test_name_exp).keys()


@pytest.mark.skipif('SKIP_LONG_RUNNING_TESTS' in os.environ, reason='Impatient developer is impatient')
def test_accurate_test_time(testdir, sleepy_test_function, simple_test_config):
    """Verify that '*_time' properties element are accurate."""

    # Expect
    test_name_exp = 'test_i_can_has_a_duration'
    sleep_seconds_exp = 2

    # Setup
    testdir.makepyfile(sleepy_test_function.format(test_name=test_name_exp, seconds=str(sleep_seconds_exp)))

    junit_xml = run_and_parse_with_config(testdir, simple_test_config)[0]

    # Test
    start = date_parser.parse(str(junit_xml.get_testcase_property(test_name_exp, 'start_time')[0]))
    end = date_parser.parse(str(junit_xml.get_testcase_property(test_name_exp, 'end_time')[0]))

    assert (end - start).seconds == sleep_seconds_exp
