# -*- coding: utf-8 -*-

"""Test cases for using pytest classes as a representation of a test case with test steps."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
from tests.conftest import run_and_parse, merge_dicts


# ======================================================================================================================
# Tests
# ======================================================================================================================
def test_class_without_steps(testdir, properly_decorated_test_method):
    """Verify that decorating a pytest class with 'test_case_with_steps' mark will declare all test functions as steps
    which inherit the parent classes marks.
    """

    # Expect
    test_name_exp = 'test_method'
    test_id_exp = 'test_case_class_id'
    jira_id_exp = 'ASC-123'

    # Setup
    testdir.makepyfile(properly_decorated_test_method.format(test_name=test_name_exp,
                                                             test_id=test_id_exp,
                                                             jira_id=jira_id_exp))

    junit_xml = run_and_parse(testdir)

    # Test
    assert junit_xml.get_testcase_properties(test_name_exp)['test_step'] == 'false'
    assert junit_xml.get_testcase_properties(test_name_exp)['test_id'] == test_id_exp
    assert junit_xml.get_testcase_properties(test_name_exp)['jira'] == jira_id_exp


def test_improperly_decorated_class_without_steps(testdir, improperly_decorated_test_method):
    """Verify that decorating a pytest class with 'test_case_with_steps' mark will declare all test functions as steps
    which inherit the parent classes marks.
    """

    # Expect
    test_name_exp = 'test_method'
    test_id_exp = 'test_case_class_id'
    jira_id_exp = 'ASC-123'

    # Setup
    testdir.makepyfile(improperly_decorated_test_method.format(test_name=test_name_exp,
                                                               test_id=test_id_exp,
                                                               jira_id=jira_id_exp))

    junit_xml = run_and_parse(testdir)

    # Test
    assert junit_xml.get_testcase_properties(test_name_exp)['test_step'] == 'false'
    assert junit_xml.get_testcase_properties(test_name_exp)['test_id'] == test_id_exp
    assert junit_xml.get_testcase_properties(test_name_exp)['jira'] == jira_id_exp


def test_class_with_steps(testdir, properly_decorated_test_class_with_steps):
    """Verify that decorating a pytest class with 'test_case_with_steps' mark will declare all test functions as steps
    which inherit the parent classes marks.
    """

    # Expect
    test_steps = {'test_step_one': 'test_step_one',
                  'test_step_two': 'test_step_two',
                  'test_step_three': 'test_step_three'}
    expectations = {'test_name': 'TestCaseWithSteps',
                    'test_id': 'test_case_class_id',
                    'jira_id': 'ASC-123'}

    # Setup
    testdir.makepyfile(properly_decorated_test_class_with_steps.format(**merge_dicts(test_steps, expectations)))

    junit_xml = run_and_parse(testdir)

    # Test
    for test_step in test_steps.values():
        assert junit_xml.get_testcase_properties(test_step)['test_step'] == 'true'
        assert junit_xml.get_testcase_properties(test_step)['test_id'] == expectations['test_id']
        assert junit_xml.get_testcase_properties(test_step)['jira'] == expectations['jira_id']


def test_class_with_steps_and_repeated_marks(testdir, improperly_decorated_test_class_with_steps):
    """Verify that decorating a pytest class with 'test_case_with_steps' mark along with marking methods of said class
    with 'test_id' and 'jira' marks will result in test cases being marked with the PARENT classes 'test_id' and 'jira'
    marks.

    Basically, we're validating that decorating test class methods with marks are ignored when the class itself is
    decorated with the 'test_case_with_steps' mark.
    """

    # Expect
    test_steps = {'test_step_one': 'test_step_one',
                  'test_step_two': 'test_step_two',
                  'test_step_three': 'test_step_three'}
    expectations = {'test_name': 'TestCaseWithSteps',
                    'test_id': 'test_case_class_id',
                    'jira_id': 'ASC-123'}

    # Setup
    testdir.makepyfile(improperly_decorated_test_class_with_steps.format(**merge_dicts(test_steps, expectations)))

    junit_xml = run_and_parse(testdir)

    # Test
    for test_step in test_steps.values():
        assert junit_xml.get_testcase_properties(test_step)['test_step'] == 'true'
        assert junit_xml.get_testcase_properties(test_step)['test_id'] == expectations['test_id']
        assert junit_xml.get_testcase_properties(test_step)['jira'] == expectations['jira_id']