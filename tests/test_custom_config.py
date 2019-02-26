# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import os
from tests.conftest import run_and_parse, run_and_parse_with_ini_config


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
    args = ["--pytest-zigzag-config", simple_test_config]
    junit_xml = run_and_parse(testdir, 0, args)[0]

    # Test
    assert junit_xml.testsuite_props


def test_config_value_overrides(testdir, single_decorated_test_function, tmpdir_factory):
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
    config_path = tmpdir_factory.mktemp('data').join('config.json').strpath

    config = \
"""
{
  "pytest_zigzag_env_vars": {
    "BUILD_URL": "foo",
    "BUILD_NUMBER": null
  }
}
"""  # noqa

    with open(config_path, 'w') as f:
        f.write(config)

    args = ["--pytest-zigzag-config", config_path]
    junit_xml = run_and_parse(testdir, 0, args)[0]

    # Test
    assert junit_xml.testsuite_props['BUILD_URL'] == 'bar'
    del os.environ['BUILD_URL']


def test_custom_config_value(testdir, single_decorated_test_function, tmpdir_factory):
    """Ensure that a value set in the config will end up as a property in xml."""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))

    config_path = tmpdir_factory.mktemp('data').join('config.json').strpath
    config = \
"""
{
  "pytest_zigzag_env_vars": {
    "BUILD_URL": "foo",
    "BUILD_NUMBER": null
  }
}
"""  # noqa

    with open(config_path, 'w') as f:
        f.write(config)

    args = ["--pytest-zigzag-config", config_path]
    junit_xml = run_and_parse(testdir, 0, args)[0]

    # Test
    assert junit_xml.testsuite_props['BUILD_URL'] == 'foo'


def test_malformed_custom_config(testdir, single_decorated_test_function, tmpdir_factory):
    """Ensure failure given a malformed json doc."""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))

    config_path = tmpdir_factory.mktemp('data').join('config.json').strpath
    config = \
"""
{
  "pytest_zigzag_env_vars": {
    "BUILD_URL": "foo",
    "BUILD_NUMBER": null,
  }
}
"""  # noqa

    with open(config_path, 'w') as f:
        f.write(config)

    args = ["--pytest-zigzag-config", config_path]
    result = run_and_parse(testdir, 1, args)

    # Test
    assert 'config file is not valid JSON' in result[1].stderr.lines[0]


def test_custom_properties_in_custom_config(testdir, single_decorated_test_function, tmpdir_factory):
    """Test that a custom config with non-standard parameters can be used."""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    config_path = tmpdir_factory.mktemp('data').join('config.json').strpath
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
"""  # noqa

    with open(config_path, 'w') as f:
        f.write(config)

    args = ["--pytest-zigzag-config", config_path]
    result = run_and_parse(testdir, 0, args)

    # Test
    assert result[0].testsuite_props['FOO'] == 'foo'
    assert result[0].testsuite_props['BAR'] == 'bar'


def test_custom_config_precidence(testdir, single_decorated_test_function, tmpdir_factory):
    """Test that a config specified on the CLI is used over one specified in the ini config"""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    cli_config_path = tmpdir_factory.mktemp('data').join('config.json').strpath
    ini_config_path = tmpdir_factory.mktemp('data').join('config.json').strpath
    json_config_cli = \
"""
{
  "pytest_zigzag_env_vars": {
    "FOO": "foo"
  }
}
""" # noqa

    json_config_ini = \
"""
{
  "pytest_zigzag_env_vars": {
    "FOO": "bar"
  }
}
"""  # noqa

    with open(cli_config_path, 'w') as f:
        f.write(json_config_cli)

    with open(ini_config_path, 'w') as f:
        f.write(json_config_ini)

    ini_config = \
"""
[pytest]
pytest-zigzag-config={}

""".format(ini_config_path)  # noqa

    args = ["--pytest-zigzag-config", cli_config_path]
    result = run_and_parse_with_ini_config(testdir, ini_config, 0, args)

    # Test
    assert result[0].testsuite_props['FOO'] == 'foo'


def test_required_parameters_are_required(testdir, single_decorated_test_function, tmpdir_factory):
    """Test that a config missing required params will fail."""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    config_path = tmpdir_factory.mktemp('data').join('config.json').strpath
    config = \
"""
{
  "not_pytest_zigzag_env_vars": {
    "BUILD_NUMBER": null
  }
}
"""  # noqa

    with open(config_path, 'w') as f:
        f.write(config)

    args = ["--pytest-zigzag-config", config_path]
    result = run_and_parse(testdir, 1, args)

    # Test
    assert "does not comply with schema:" in result[1].stderr.lines[0]
    assert "'pytest_zigzag_env_vars' is a required property" in result[1].stderr.lines[0]


def test_default_config(testdir, single_decorated_test_function):
    """Test that a default config is present if none is configured"""

    # Expect
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'

    # Setup
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    args = []  # no config is provided
    junit_xml = run_and_parse(testdir, 0, args)[0]

    # Test
    assert 'BUILD_NUMBER' in junit_xml.testsuite_props  # if there was no config we would not have a BUILD_NUMBER
