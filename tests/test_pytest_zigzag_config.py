# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
import pytest
from json import dump
# noinspection PyProtectedMember
from _pytest.outcomes import Exit
# noinspection PyProtectedMember
from pytest_zigzag import _load_config_file


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
@pytest.fixture(scope='module')
def invalid_pytest_zigzag_json_config(tmpdir_factory):
    """Create an invalid 'pytest-zigzag-config' on disk.

    Args:
        tmpdir_factory (_pytest.tmpdir.TempdirFactory): Create a temp directory.

    Returns:
        str: Path to config file.
    """

    config = {
        "not_quite_right":
            [
                "var1",
                "var2",
                "var3"
            ]
    }

    config_path = tmpdir_factory.mktemp('data').join('invalid_config.json').strpath
    with open(str(config_path), 'w') as f:
        dump(config, f)

    return config_path


@pytest.fixture(scope='module')
def invalid_json_file(tmpdir_factory):
    """Create an invalid JSON on disk.

    Args:
        tmpdir_factory (_pytest.tmpdir.TempdirFactory): Create a temp directory.

    Returns:
        str: Path to config file.
    """

    config_path = tmpdir_factory.mktemp('data').join('invalid.json').strpath
    with open(str(config_path), 'w') as f:
        f.write('!!!!This is not valid json!!!!!')

    return config_path


@pytest.fixture(scope='module')
def valid_json_file_with_job_name(tmpdir_factory):
    """Create a valid JSON on disk.

    Args:
        tmpdir_factory (_pytest.tmpdir.TempdirFactory): Create a temp directory.

    Returns:
        str: Path to config file.
    """

    config_path = tmpdir_factory.mktemp('data').join('valid.json').strpath
    with open(str(config_path), 'w') as f:
        f.write("""
{
  "environment_variables": {
    "BUILD_URL": null,
    "BUILD_NUMBER": null,
    "RE_JOB_ACTION": null,
    "RE_JOB_IMAGE": null,
    "RE_JOB_SCENARIO": null,
    "RE_JOB_BRANCH": null,
    "RPC_RELEASE": null,
    "RPC_PRODUCT_RELEASE": null,
    "OS_ARTIFACT_SHA": null,
    "PYTHON_ARTIFACT_SHA": null,
    "APT_ARTIFACT_SHA": null,
    "REPO_URL": null,
    "JOB_NAME": "foo",
    "MOLECULE_TEST_REPO": null,
    "MOLECULE_SCENARIO_NAME": null,
    "MOLECULE_GIT_COMMIT": null
  }
}
                """)

    return config_path


# ======================================================================================================================
# Tests
# ======================================================================================================================
def test_invalid_config_file(invalid_pytest_zigzag_json_config):
    """Verify that config files that do not comply with the schema are rejected.

    Args:
        invalid_pytest_zigzag_json_config (str): Path to config file.
    """

    # Expect
    error_msg = 'does not comply with schema:'

    # Test
    with pytest.raises(Exit) as e:
        _load_config_file(invalid_pytest_zigzag_json_config)

    assert error_msg in str(e)


def test_invalid_json_config_file(invalid_json_file):
    """Verify that config files that do not contain valid JSON are rejected.

    Args:
        invalid_json_file (str): Path to config file.
    """

    # Expect
    error_msg = 'file is not valid JSON'

    # Test
    with pytest.raises(Exit) as e:
        _load_config_file(invalid_json_file)

    assert error_msg in str(e)


def test_valid_json_config_file(valid_json_file_with_job_name):
    """Verify that config files that contain valid JSON are not rejected.

    Args:
        valid_json_file_with_job_name (str): Path to config file.
    """

    # Test
    _load_config_file(valid_json_file_with_job_name)


def test_valid_json_config_file_string(valid_json_file_with_job_name):
    """Verify that config files can be customized.

    Args:
        valid_json_file_with_job_name(str): Path to config file.
    """

    # Test
    config_dict = _load_config_file(valid_json_file_with_job_name)

    assert config_dict['environment_variables']['JOB_NAME'] == "foo"


def test_invalid_config_file_path():
    """Verify that an invalid config file path is rejected."""

    # Expect
    error_msg = 'Failed to load'

    # Test
    with pytest.raises(Exit) as e:
        _load_config_file('/path/does/not/exist')

    assert error_msg in str(e)
