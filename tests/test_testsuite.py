# -*- coding: utf-8 -*-

"""Test cases for the 'pytest_runtestloop' hook function for collecting environment variables"""

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import os
# noinspection PyProtectedMember
from pytest_zigzag import _load_config_file
from tests.conftest import is_sub_dict, run_and_parse_with_config, build_property_list

# ======================================================================================================================
# Globals
# ======================================================================================================================
config_file = './pytest_zigzag/data/configs/default-config.json'
ASC_TEST_ENV_VARS = build_property_list(_load_config_file(config_file))  # Shallow copy.

# ======================================================================================================================
# Tests
# ======================================================================================================================


def test_no_env_vars_set(testdir, undecorated_test_function, testsuite_attribs_exp, simple_test_config):
    """Verify that pytest accepts our fixture without setting any environment variables."""

    # Setup
    testdir.makepyfile(undecorated_test_function.format(test_name='test_pass'))

    junit_xml = run_and_parse_with_config(testdir, simple_test_config)[0]

    # Test
    assert is_sub_dict(testsuite_attribs_exp, junit_xml.testsuite_attribs)

    for env_var in ASC_TEST_ENV_VARS:
        assert junit_xml.testsuite_props[env_var] == 'None' or '[]'


def test_env_vars_set(testdir, undecorated_test_function, testsuite_attribs_exp, simple_test_config):
    """Verify that pytest accepts our fixture with all relevant environment variables set."""

    # Setup
    testdir.makepyfile(undecorated_test_function.format(test_name='test_pass'))

    for env in ASC_TEST_ENV_VARS:
        os.environ[env] = env

    junit_xml = run_and_parse_with_config(testdir, simple_test_config)[0]

    # Test
    assert is_sub_dict(testsuite_attribs_exp, junit_xml.testsuite_attribs)

    expected = {env: env for env in ASC_TEST_ENV_VARS}
    assert junit_xml.testsuite_props == expected
