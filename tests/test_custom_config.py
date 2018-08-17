# -*- coding: utf-8 -*-


# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
from tests.conftest import run_and_parse_with_config
from tests.conftest import JunitXml
import re


# ======================================================================================================================
# Tests
# ======================================================================================================================
def test_config_asc(testdir, single_decorated_test_function):
    """Verify that 'ci-environment' with a value of 'asc' can be supplied in the config"""

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
[pytest]
ci-environment=asc
"""  # noqa

    junit_xml = run_and_parse_with_config(testdir, config)

    # Test
    assert 'ci-environment' in junit_xml.testsuite_props
    assert junit_xml.testsuite_props['ci-environment'] == 'asc'


def test_config_mk8s(testdir, single_decorated_test_function):
    """Verify that 'ci-environment' with a value of 'mk8s' can be supplied in the config"""

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
[pytest]
ci-environment=mk8s
"""  # noqa

    junit_xml = run_and_parse_with_config(testdir, config)

    # Test
    assert 'ci-environment' in junit_xml.testsuite_props
    assert junit_xml.testsuite_props['ci-environment'] == 'mk8s'


def test_config_default(testdir, single_decorated_test_function):
    """Verify the default value for 'ci-environment'"""

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
[pytest]
"""  # noqa

    junit_xml = run_and_parse_with_config(testdir, config)

    # Test
    assert 'ci-environment' in junit_xml.testsuite_props
    assert junit_xml.testsuite_props['ci-environment'] == 'asc'


def test_cli_trumps_config(testdir, single_decorated_test_function):
    """Verify that 'ci-environment' passed via the CLI has the highest precedence"""

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
[pytest]
ci-environment=asc
"""  # noqa

    result_path = testdir.tmpdir.join('junit.xml')
    config_path = testdir.tmpdir.join('conf.conf')
    with open(str(config_path), 'w') as f:
        f.write(config)

    result = testdir.runpytest(
        "--junitxml={}".format(result_path), "-c={}".format(config_path), "--ci-environment=mk8s")

    assert result.ret == 0

    junit_xml = JunitXml(str(result_path))

    # Test
    assert 'ci-environment' in junit_xml.testsuite_props
    assert junit_xml.testsuite_props['ci-environment'] == 'mk8s'


def test_unknown_value(testdir, single_decorated_test_function):
    """Verify the default value for 'ci-environment'"""

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
[pytest]
ci-environment=foobar
"""  # noqa

    result_path = testdir.tmpdir.join('junit.xml')
    config_path = testdir.tmpdir.join('conf.conf')
    with open(str(config_path), 'w') as f:
        f.write(config)

    result = testdir.runpytest("--junitxml={}".format(result_path), "-c={}".format(config_path))

    out_lines = [str(x) for x in result.outlines]
    expected_error = re.compile('.*RuntimeError: The value foobar is not a valid value.*')
    assert any(re.match(expected_error, x) for x in out_lines)
