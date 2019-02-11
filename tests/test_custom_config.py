# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import os
from tests.conftest import run_and_parse_with_config


# ======================================================================================================================
# Tests
# ======================================================================================================================
def test_custom_config(testdir, single_decorated_test_function, simple_test_config):
    """Ensure that we can use a known good json document."""

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
    assert junit_xml.testsuite_props


def test_config_value_overrides(testdir, single_decorated_test_function):
    """Ensure that a value set as an environment var will override a value in the config file."""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    os.environ["BUILD_URL"] = "bar"

    config = \
"""
{
  "pytest_zigzag_env_vars": {
    "BUILD_URL": "foo",
    "BUILD_NUMBER": null
  }
}
""" # noqa

    junit_xml = run_and_parse_with_config(testdir, config)[0]

    # Test
    assert junit_xml.testsuite_props['BUILD_URL'] == 'bar'
    del os.environ['BUILD_URL']


def test_custom_config_value(testdir, single_decorated_test_function):
    """Ensure that a value set in the config will end up as a property in xml."""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    config = \
"""
{
  "pytest_zigzag_env_vars": {
    "BUILD_URL": "foo",
    "BUILD_NUMBER": null
  }
}
""" # noqa

    junit_xml = run_and_parse_with_config(testdir, config)[0]

    # Test
    assert junit_xml.testsuite_props['BUILD_URL'] == 'foo'


def test_malformed_custom_config(testdir, single_decorated_test_function):
    """Ensure failure given a malformed json doc."""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    config = \
"""
{
  "pytest_zigzag_env_vars": {
    "BUILD_URL": "foo",
    "BUILD_NUMBER": null,
  }
}
""" # noqa

    result = run_and_parse_with_config(testdir, config, exit_code_exp=1)

    # Test
    assert 'config file is not valid JSON' in result[1].stderr.lines[0]


def test_custom_properties_in_custom_config(testdir, single_decorated_test_function):
    """Test that a custom config with non-standard parameters can be used."""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    config = \
"""
{
  "pytest_zigzag_env_vars": {
    "FOO": "foo",
    "BAR": "bar",
    "BUILD_URL": "foo",
    "BUILD_NUMBER": null
  }
}
""" # noqa

    result = run_and_parse_with_config(testdir, config)

    # Test
    assert result[0].testsuite_props['FOO'] == 'foo'
    assert result[0].testsuite_props['BAR'] == 'bar'


def test_custom_config_precidence(testdir, single_decorated_test_function):
    """Test that a custom config with non-standard parameters can be used."""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    json_config = \
"""
{
  "pytest_zigzag_env_vars": {
    "FOO": "foo",
    "BAR": "bar",
    "BUILD_URL": "foo",
    "BUILD_NUMBER": null
  }
}
""" # noqa

    ini_config = "[pytest]\n"

    result = run_and_parse_with_config(testdir, json_config, 0, None, ini_config)

    # Test
    assert result[0].testsuite_props['FOO'] == 'foo'
    assert result[0].testsuite_props['BAR'] == 'bar'


def test_required_parameters_are_required(testdir, single_decorated_test_function):
    """Test that a config missing required params will fail."""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    config = \
"""
{
  "not_pytest_zigzag_env_vars": {
    "BUILD_NUMBER": null
  }
}
""" # noqa

    result = run_and_parse_with_config(testdir, config, exit_code_exp=1)

    # Test
    assert "does not comply with schema:" in result[1].stderr.lines[0]
    assert "'pytest_zigzag_env_vars' is a required property" in result[1].stderr.lines[0]
