# -*- coding: utf-8 -*-

"""Test cases for using pytest classes as a representation of a test case with test steps."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
from tests.conftest import merge_dicts, is_sub_dict, run_and_parse


# ======================================================================================================================
# Tests
# ======================================================================================================================
def test_class_without_steps(testdir, properly_decorated_test_method, simple_test_config):
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

    args = ["--pytest-zigzag-config", simple_test_config]
    junit_xml = run_and_parse(testdir, 0, args)[0]

    # Test
    assert junit_xml.get_testcase_properties(test_name_exp)['test_step'] == 'false'
    assert junit_xml.get_testcase_properties(test_name_exp)['test_id'] == test_id_exp
    assert junit_xml.get_testcase_properties(test_name_exp)['jira'] == jira_id_exp


def test_improperly_decorated_class_without_steps(testdir, improperly_decorated_test_method, simple_test_config):
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

    args = ["--pytest-zigzag-config", simple_test_config]
    junit_xml = run_and_parse(testdir, 0, args)[0]

    # Test
    assert junit_xml.get_testcase_properties(test_name_exp)['test_step'] == 'false'
    assert junit_xml.get_testcase_properties(test_name_exp)['test_id'] == test_id_exp
    assert junit_xml.get_testcase_properties(test_name_exp)['jira'] == jira_id_exp


def test_class_with_steps(testdir, properly_decorated_test_class_with_steps, simple_test_config):
    """Verify that decorating a pytest class with 'test_case_with_steps' mark will declare all test functions as steps
    which inherit the parent classes marks.
    """

    # Expect
    test_steps = {'test_step_one': 'test_step_one',
                  'test_step_two': 'test_step_two',
                  'test_step_three': 'test_step_three'}
    tc_props_exps = {'test_name': 'TestCaseWithSteps',
                     'test_id': 'test_case_class_id',
                     'jira_id': 'ASC-123'}

    # Setup
    testdir.makepyfile(properly_decorated_test_class_with_steps.format(**merge_dicts(test_steps, tc_props_exps)))

    args = ["--pytest-zigzag-config", simple_test_config]
    junit_xml = run_and_parse(testdir, 0, args)[0]

    # Test
    for test_step in test_steps.values():
        assert junit_xml.get_testcase_properties(test_step)['test_step'] == 'true'
        assert junit_xml.get_testcase_properties(test_step)['test_id'] == tc_props_exps['test_id']
        assert junit_xml.get_testcase_properties(test_step)['jira'] == tc_props_exps['jira_id']


def test_class_with_steps_and_repeated_marks(testdir, improperly_decorated_test_class_with_steps, simple_test_config):
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
    tc_props_exps = {'test_name': 'TestCaseWithSteps',
                     'test_id': 'test_case_class_id',
                     'jira_id': 'ASC-123'}

    # Setup
    testdir.makepyfile(improperly_decorated_test_class_with_steps.format(**merge_dicts(test_steps, tc_props_exps)))

    args = ["--pytest-zigzag-config", simple_test_config]
    junit_xml = run_and_parse(testdir, 0, args)[0]

    # Test
    for test_step in test_steps.values():
        assert junit_xml.get_testcase_properties(test_step)['test_step'] == 'true'
        assert junit_xml.get_testcase_properties(test_step)['test_id'] == tc_props_exps['test_id']
        assert junit_xml.get_testcase_properties(test_step)['jira'] == tc_props_exps['jira_id']


def test_class_with_failed_step(testdir, properly_decorated_test_class_with_step_failure, simple_test_config):
    """Verify that steps that follow a failing step will automatically skip."""

    # Expect
    test_steps = {'test_step_one': 'test_step_one',
                  'test_step_two': 'test_step_fail',
                  'test_step_three': 'test_step_skip',
                  'test_step_four': 'test_step_skip_again'}
    tc_props_exps = {'test_name': 'TestCaseWithSteps',
                     'test_id': 'test_case_class_id',
                     'jira_id': 'ASC-123'}
    ts_attribs_exps = {'tests': '4',
                       'errors': '0',
                       'skips': '2',
                       'failures': '1'}
    # Setup
    testdir.makepyfile(properly_decorated_test_class_with_step_failure.format(**merge_dicts(test_steps, tc_props_exps)))

    args = ["--pytest-zigzag-config", simple_test_config]
    junit_xml = run_and_parse(testdir, 1, args)[0]

    # Test
    assert is_sub_dict(ts_attribs_exps, junit_xml.testsuite_attribs)

    for test_step in test_steps.values():
        assert junit_xml.get_testcase_properties(test_step)['test_step'] == 'true'
        assert junit_xml.get_testcase_properties(test_step)['test_id'] == tc_props_exps['test_id']
        assert junit_xml.get_testcase_properties(test_step)['jira'] == tc_props_exps['jira_id']


def test_class_with_setup_steps(testdir, properly_decorated_test_class_with_step_failure, simple_test_config):
    """Verify that steps with 'setup' in the name will always be ran regardless if previous steps failed."""

    # Expect
    test_steps = {'test_step_one': 'test_setup_one',
                  'test_step_two': 'test_fail',
                  'test_step_three': 'test_skip',
                  'test_step_four': 'test_setup_two'}
    tc_props_exps = {'test_name': 'TestCaseWithSteps',
                     'test_id': 'test_case_class_id',
                     'jira_id': 'ASC-123'}
    ts_attribs_exps = {'tests': '4',
                       'errors': '0',
                       'skips': '1',
                       'failures': '1'}
    # Setup
    testdir.makepyfile(properly_decorated_test_class_with_step_failure.format(**merge_dicts(test_steps, tc_props_exps)))

    args = ["--pytest-zigzag-config", simple_test_config]
    junit_xml = run_and_parse(testdir, 1, args)[0]

    # Test
    assert is_sub_dict(ts_attribs_exps, junit_xml.testsuite_attribs)

    for test_step in test_steps.values():
        assert junit_xml.get_testcase_properties(test_step)['test_step'] == 'true'
        assert junit_xml.get_testcase_properties(test_step)['test_id'] == tc_props_exps['test_id']
        assert junit_xml.get_testcase_properties(test_step)['jira'] == tc_props_exps['jira_id']


def test_class_with_teardown_steps(testdir, properly_decorated_test_class_with_step_failure, simple_test_config):
    """Verify that steps with 'teardown' in the name will always be ran regardless if previous steps failed."""

    # Expect
    test_steps = {'test_step_one': 'test_teardown_one',
                  'test_step_two': 'test_fail',
                  'test_step_three': 'test_skip',
                  'test_step_four': 'test_teardown_two'}
    tc_props_exps = {'test_name': 'TestCaseWithSteps',
                     'test_id': 'test_case_class_id',
                     'jira_id': 'ASC-123'}
    ts_attribs_exps = {'tests': '4',
                       'errors': '0',
                       'skips': '1',
                       'failures': '1'}
    # Setup
    testdir.makepyfile(properly_decorated_test_class_with_step_failure.format(**merge_dicts(test_steps, tc_props_exps)))

    args = ["--pytest-zigzag-config", simple_test_config]
    junit_xml = run_and_parse(testdir, 1, args)[0]

    # Test
    assert is_sub_dict(ts_attribs_exps, junit_xml.testsuite_attribs)

    for test_step in test_steps.values():
        assert junit_xml.get_testcase_properties(test_step)['test_step'] == 'true'
        assert junit_xml.get_testcase_properties(test_step)['test_id'] == tc_props_exps['test_id']
        assert junit_xml.get_testcase_properties(test_step)['jira'] == tc_props_exps['jira_id']


def test_class_with_setup_and_teardown_steps(testdir,
                                             properly_decorated_test_class_with_step_failure,
                                             simple_test_config):
    """Verify that steps with 'setup' or 'teardown' in the name will always be ran regardless if previous steps failed.
    """

    # Expect
    test_steps = {'test_step_one': 'test_setup',
                  'test_step_two': 'test_fail',
                  'test_step_three': 'test_skip',
                  'test_step_four': 'test_teardown'}
    tc_props_exps = {'test_name': 'TestCaseWithSteps',
                     'test_id': 'test_case_class_id',
                     'jira_id': 'ASC-123'}
    ts_attribs_exps = {'tests': '4',
                       'errors': '0',
                       'skips': '1',
                       'failures': '1'}
    # Setup
    testdir.makepyfile(properly_decorated_test_class_with_step_failure.format(**merge_dicts(test_steps, tc_props_exps)))

    args = ["--pytest-zigzag-config", simple_test_config]
    junit_xml = run_and_parse(testdir, 1, args)[0]

    # Test
    assert is_sub_dict(ts_attribs_exps, junit_xml.testsuite_attribs)

    for test_step in test_steps.values():
        assert junit_xml.get_testcase_properties(test_step)['test_step'] == 'true'
        assert junit_xml.get_testcase_properties(test_step)['test_id'] == tc_props_exps['test_id']
        assert junit_xml.get_testcase_properties(test_step)['jira'] == tc_props_exps['jira_id']
