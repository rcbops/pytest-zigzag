# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest
from lxml import etree
pytest_plugins = ['pytester']


# ======================================================================================================================
# Classes
# ======================================================================================================================
class JunitXml(object):
    """A helper class for obtaining elements from JUnitXML result files produced by pytest-zigzag."""

    def __init__(self, xml_file_path):
        """Create a JunitXML class object.

        Args:
            xml_file_path (str): A file path to a JUnitXML file created using the pytest-zigzag plug-in.
        """

        self._xml_file_path = xml_file_path
        self._xml_doc = etree.parse(xml_file_path).getroot()

        self._testsuite_props = None
        self._testsuite_attribs = None

    @property
    def testsuite_props(self):
        """dict: A dictionary of properties on the testsuite root element."""

        if not self._testsuite_props:
            self._testsuite_props = {p.attrib['name']: p.attrib['value']
                                     for p in self._xml_doc.findall('./properties/property')}

        return self._testsuite_props

    @property
    def testsuite_attribs(self):
        """dict: A dictionary of attributes on the testsuite root element."""

        if not self._testsuite_attribs:
            self._testsuite_attribs = dict(self._xml_doc.attrib)

        return self._testsuite_attribs

    @property
    def xml_doc(self):
        """lxml.etree.Element: Raw etree doc at the testsuite root element."""

        return self._xml_doc

    def get_testcase_property(self, testcase_name, property_name):
        """Retrieve all the properties for a specified testcase.

        Args:
            testcase_name (str): The name of the desired testcase from which to retrieve properties.
            property_name (str): The name of the desired property.

        Returns:
            list: A list of values for the specified property name.
        """

        xpath = "./testcase/[@name='{}']/properties/property/[@name='{}']".format(testcase_name, property_name)

        return [p.attrib['value'] for p in self._xml_doc.findall(xpath)]

    def get_testcase_properties(self, testcase_name):
        """Retrieve all the properties for a specified testcase.

        Note: if there are multiple properties with the same name only one of the values will be returned.

        Args:
            testcase_name (str): The name of the desired testcase from which to retrieve properties.

        Returns:
            dict: A dictionary of properties on the specified testcase element.
        """

        xpath = "./testcase/[@name='{}']/properties/property".format(testcase_name)

        return {p.attrib['name']: p.attrib['value'] for p in self._xml_doc.findall(xpath)}


# ======================================================================================================================
# Helpers
# ======================================================================================================================
def is_sub_dict(small, big):
    """Determine if one dictionary is a subset of another dictionary.

    Args:
        small (dict): A dictionary that is proposed to be a subset of another dictionary.
        big (dict): A dictionary that is a superset of another dictionary.

    Returns:
        bool: A bool indicating if the small dictionary is in fact a sub-dictionary of big
    """

    return dict(big, **small) == big


def run_and_parse(testdir, exit_code_exp=0, runpytest_args=None):
    """Execute a pytest run against a directory containing pytest Python files.

    Args:
        testdir (_pytest.pytester.TestDir): A pytest fixture for testing pytest plug-ins.
        exit_code_exp (int): The expected exit code for pytest run. (Default = 0)
        runpytest_args (list(object)): A list of positional arguments to pass into the "testdir" fixture.
            (Default = [])

    Returns:
        tuple: [(JunitXml: A wrapper class for the etree element at the root of the supplied JUnitXML file.),
                (the pytest result object)]
    """

    runpytest_args = [] if not runpytest_args else runpytest_args
    result_path = testdir.tmpdir.join('junit.xml')
    result = testdir.runpytest("--junitxml={}".format(result_path), *runpytest_args)

    assert result.ret == exit_code_exp

    junit_xml_doc = JunitXml(str(result_path))

    return junit_xml_doc, result


def run_and_parse_with_ini_config(testdir, config, exit_code_exp=0, runpytest_args=None):
    """Execute a pytest run against a directory containing pytest Python files.
    Args:
        testdir (_pytest.pytester.TestDir): A pytest fixture for testing pytest plug-ins.
        config (str): The contents of the pytest.ini config that you want to use.
        exit_code_exp (int): The expected exit code for pytest run. (Default = 0)
        runpytest_args (list(object)): A list of positional arguments to pass into the "testdir" fixture.
            (Default = [])
    Returns:
        tuple: [(JunitXml: A wrapper class for the etree element at the root of the supplied JUnitXML file.),
                (the pytest result object)]
    """

    runpytest_args = [] if not runpytest_args else runpytest_args
    result_path = testdir.tmpdir.join('junit.xml')
    config_path = testdir.tmpdir.join('conf.conf')
    with open(str(config_path), 'w') as f:
        f.write(config)

    result = testdir.runpytest("--junitxml={}".format(result_path), "-c={}".format(config_path), *runpytest_args)

    assert result.ret == exit_code_exp

    junit_xml_doc = JunitXml(str(result_path))

    return junit_xml_doc, result


def build_property_list(config_dict):
    """ Build a list of properties and values that will end up in junit xml. This should only
        be used for testing purposes to set expectations.

    Args:
        config_dict: a python object representation of pytest_zigzag config json

    Returns:
        props: a flattened dictionary of properties and values
    """
    props = {}
    for root_key in config_dict:
        if not config_dict[root_key] is None:
            for key in config_dict[root_key]:
                props[key] = config_dict[root_key][key]
    return props


def merge_dicts(*args):
    """Given any number of dicts, shallow copy and merge into a new dict, precedence goes to key value pairs in latter
    dicts.

    Args:
        *args (list(dict)): A list of dictionaries to be merged.

    Returns:
        dict: A merged dictionary.
    """

    result = {}
    for dictionary in args:
        result.update(dictionary)
    return result


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
@pytest.fixture(scope='session')
def testsuite_attribs_exp():
    """A common set of testsuite attributes shared across many test cases."""

    return {'tests': '1', 'errors': '0', 'name': 'pytest', 'skips': '0', 'failures': '0'}


@pytest.fixture(scope='session')
def undecorated_test_function():
    """An undecorated Python function that simple passes with the following named formatters:

        test_name: Name of undecorated function.
    """

    py_file = \
        """
        import pytest
        def {test_name}():
            pass
        """

    return py_file


@pytest.fixture(scope='session')
def single_decorated_test_function():
    """A Python function decorated with a single pytest mark with the following named formatters:

        test_name: Name of decorated function.
        mark_type: The name of the pytest mark.
        mark_arg: The value for the pytest mark.
    """

    py_file = \
        """
        import pytest
        @pytest.mark.{mark_type}('{mark_arg}')
        def {test_name}():
            pass
        """

    return py_file


@pytest.fixture(scope='session')
def properly_decorated_test_function():
    """A Python function decorated with the required 'test_id' and 'jira' marks along with the following named
    formatters:

        test_name: Name of decorated function.
        test_id: The desired 'test_id' mark argument.
        jira_id: The desired 'jira' mark argument.
    """

    py_file = \
        """
        import pytest
        @pytest.mark.test_id('{test_id}')
        @pytest.mark.jira('{jira_id}')
        def {test_name}():
            pass
        """

    return py_file


@pytest.fixture(scope='session')
def properly_decorated_test_method():
    """A Python method decorated with the required 'test_id' and 'jira' marks without the class being decorated with the
    'test_case_with_steps' mark.

    Named formatters:

        test_name: Name of decorated function.
        test_id: The desired 'test_id' mark argument.
        jira_id: The desired 'jira' mark argument.
    """

    py_file = \
        """
        import pytest
        class TestClass(object):
            @pytest.mark.test_id('{test_id}')
            @pytest.mark.jira('{jira_id}')
            def {test_name}(self):
                pass
        """

    return py_file


@pytest.fixture(scope='session')
def improperly_decorated_test_method():
    """A Python method decorated with the required 'test_id' and 'jira' marks without the class being decorated with the
    'test_case_with_steps' mark, but with 'test_id' and 'jira' marks on the class.

    Named formatters:

        test_name: Name of decorated method.
        test_id: The desired 'test_id' mark argument.
        jira_id: The desired 'jira' mark argument.
    """

    py_file = \
        """
        import pytest
        @pytest.mark.test_id('{test_id}')
        @pytest.mark.jira('{jira_id}')
        class TestClass(object):
            @pytest.mark.test_id('Uhh oh!')
            @pytest.mark.jira('BAD-123')
            def {test_name}(self):
                pass
        """

    return py_file


@pytest.fixture(scope='session')
def properly_decorated_test_class_with_steps():
    """A Python class decorated with the 'test_case_with_steps' mark which designates it as a test case with steps. The
    class is also decorate with the required 'test_id', 'jira' marks.

    Named formatters:

        test_name: Name of decorated class. (Test case name)
        test_step_one: Name of the first decorated function within the class.
        test_step_two: Name of the second decorated function within the class.
        test_step_three: Name of the third decorated function within the class.
        test_id: The desired 'test_id' mark argument.
        jira_id: The desired 'jira' mark argument.
    """

    py_file = \
        """
        import pytest
        @pytest.mark.test_id('{test_id}')
        @pytest.mark.jira('{jira_id}')
        @pytest.mark.test_case_with_steps
        class {test_name}(object):
            def {test_step_one}(self):
                pass
            def {test_step_two}(self):
                pass
            def {test_step_three}(self):
                pass
        """

    return py_file


@pytest.fixture(scope='session')
def properly_decorated_test_class_with_step_failure():
    """A Python class decorated with the 'test_case_with_steps' mark which designates it as a test case with steps. The
    class is also decorate with the required 'test_id', 'jira' marks. The second test step will report a failure.

    Named formatters:

        test_name: Name of decorated class. (Test case name)
        test_step_one: Name of the first decorated function within the class.
        test_step_two: Name of the second decorated function within the class. (Will report failure)
        test_step_three: Name of the third decorated function within the class.
        test_step_four: Name of the third decorated function within the class.
        test_id: The desired 'test_id' mark argument.
        jira_id: The desired 'jira' mark argument.
    """

    py_file = \
        """
        import pytest
        @pytest.mark.test_id('{test_id}')
        @pytest.mark.jira('{jira_id}')
        @pytest.mark.test_case_with_steps
        class {test_name}(object):
            def {test_step_one}(self):
                pass
            def {test_step_two}(self):
                assert False
            def {test_step_three}(self):
                pass
            def {test_step_four}(self):
                pass
        """

    return py_file


@pytest.fixture(scope='session')
def improperly_decorated_test_class_with_steps():
    """A Python class decorated with the 'test_case_with_steps' mark which designates it as a test case with steps. The
    class is also decorate with the required 'test_id', 'jira' marks. Each method is also decorated with the 'test_id',
    'jira' marks which will be ignored.

    Named formatters:

        test_name: Name of decorated class. (Test case name)
        test_step_one: Name of the first decorated function within the class.
        test_step_two: Name of the second decorated function within the class.
        test_step_three: Name of the third decorated function within the class.
        test_id: The desired 'test_id' mark argument.
        jira_id: The desired 'jira' mark argument.
    """

    py_file = \
        """
        import pytest
        @pytest.mark.test_id('{test_id}')
        @pytest.mark.jira('{jira_id}')
        @pytest.mark.test_case_with_steps
        class {test_name}(object):
            @pytest.mark.test_id('test_step_one_test_id')
            @pytest.mark.jira('test_step_one_jira_id')
            def {test_step_one}(self):
                pass
            @pytest.mark.test_id('test_step_two_test_id')
            @pytest.mark.jira('test_step_two_jira_id')
            def {test_step_two}(self):
                pass
            @pytest.mark.test_id('test_step_three_test_id')
            @pytest.mark.jira('test_step_three_jira_id')
            def {test_step_three}(self):
                pass
        """

    return py_file


@pytest.fixture(scope='session')
def sleepy_test_function():
    """A Python function that sleeps for a period of time with the following named formatters:

        test_name: Name of decorated function.
        seconds: The number of seconds to sleep.
    """

    py_file = \
        """
        import pytest
        import time
        def {test_name}():
            time.sleep({seconds})
        """

    return py_file


@pytest.fixture(scope='session')
def failure_in_test_setup():
    """A Python function that has a fixture that fails setup with the following named formatters:

        test_name: Name of the test_function
    """

    py_file = \
        """
        import pytest
        @pytest.fixture(scope='function')
        def my_test_fixture():
            assert False
            yield
            pass
        def {test_name}(my_test_fixture):
            pass
        """

    return py_file


@pytest.fixture(scope='session')
def failure_in_test_teardown():
    """A Python function that has a fixture that fails teardown with the following named formatters:

        test_name: Name of the test_function
    """

    py_file = \
        """
        import pytest
        @pytest.fixture(scope='function')
        def my_test_fixture():
            pass
            yield
            assert False
        def {test_name}(my_test_fixture):
            pass
        """

    return py_file


@pytest.fixture(scope='session')
def simple_test_config(tmpdir_factory):
    """Provides a simple test config

    Returns:
        str: the path to a json config file
    """

    filename = tmpdir_factory.mktemp('data').join('config.json').strpath
    config = \
"""
{
  "pytest_zigzag_env_vars": {
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
    "GIT_URL": null,
    "JOB_NAME": null,
    "MOLECULE_TEST_REPO": null,
    "MOLECULE_SCENARIO_NAME": null,
    "PATH_TO_TEST_EXEC_DIR": null,
    "MOLECULE_GIT_COMMIT": null,
    "GIT_COMMIT": null
  }
}
"""  # noqa

    with open(filename, 'w') as f:
        f.write(config)

    return filename


@pytest.fixture(scope='session')
def mk8s_test_config(tmpdir_factory):
    """Provides a mk8s test config

    Returns:
        str: the path to a json config file
    """

    filename = tmpdir_factory.mktemp('data').join('mk8s_config.json').strpath
    config = \
        """
{
  "pytest_zigzag_env_vars": {
    "BUILD_URL": null,
    "BUILD_NUMBER": null,
    "BUILD_ID": null,
    "NODE_NAME": null,
    "JOB_NAME": null,
    "BUILD_TAG": null,
    "JENKINS_URL": null,
    "EXECUTOR_NUMBER": null,
    "WORKSPACE": null,
    "CVS_BRANCH": null,
    "GIT_COMMIT": null,
    "GIT_URL": null,
    "GIT_BRANCH": null,
    "GIT_LOCAL_BRANCH": null,
    "GIT_AUTHOR_NAME": null,
    "GIT_AUTHOR_EMAIL": null,
    "BRANCH_NAME": null,
    "CHANGE_AUTHOR_DISPLAY_NAME": null,
    "CHANGE_AUTHOR": null,
    "CHANGE_BRANCH": null,
    "CHANGE_FORK": null,
    "CHANGE_ID": null,
    "CHANGE_TARGET": null,
    "CHANGE_TITLE": null,
    "CHANGE_URL": null,
    "JOB_URL": null,
    "NODE_LABELS": null,
    "PATH_TO_TEST_EXEC_DIR": null,
    "PWD": null,
    "STAGE_NAME": null
  }
}
"""  # noqa

    with open(filename, 'w') as f:
        f.write(config)

    return filename


@pytest.fixture(scope='session')
def asc_test_config(tmpdir_factory):
    """Provides a mk8s test config

    Returns:
        str: the path to a json config file
    """

    filename = tmpdir_factory.mktemp('data').join('mk8s_config.json').strpath
    config = \
        """
{
  "pytest_zigzag_env_vars": {
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
    "GIT_URL": null,
    "JOB_NAME": null,
    "MOLECULE_TEST_REPO": null,
    "MOLECULE_SCENARIO_NAME": null,
    "PATH_TO_TEST_EXEC_DIR": null,
    "MOLECULE_GIT_COMMIT": null,
    "GIT_COMMIT": null
  }
}
"""  # noqa

    with open(filename, 'w') as f:
        f.write(config)

    return filename
