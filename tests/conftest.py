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


def run_and_parse(testdir, exit_code_exp=0, runpytest_args=list()):
    """Execute a pytest run against a directory containing pytest Python files.

    Args:
        testdir (_pytest.pytester.TestDir): A pytest fixture for testing pytest plug-ins.
        exit_code_exp (int): The expected exit code for pytest run. (Default = 0)
        runpytest_args (list(object)): A list of positional arguments to pass into the "testdir" fixture.
            (Default = [])

    Returns:
        JunitXml: A wrapper class for the etree element at the root of the supplied JUnitXML file.
    """

    result_path = testdir.tmpdir.join('junit.xml')
    result = testdir.runpytest("--junitxml={}".format(result_path), *runpytest_args)

    assert result.ret == exit_code_exp

    junit_xml_doc = JunitXml(str(result_path))

    return junit_xml_doc


def run_and_parse_with_config(testdir, config, exit_code_exp=0, runpytest_args=list()):
    """Execute a pytest run against a directory containing pytest Python files.

    Args:
        testdir (_pytest.pytester.TestDir): A pytest fixture for testing pytest plug-ins.
        config (str): THe contents of the config that you want to use.
        exit_code_exp (int): The expected exit code for pytest run. (Default = 0)
        runpytest_args (list(object)): A list of positional arguments to pass into the "testdir" fixture.
            (Default = [])

    Returns:
        JunitXml: A wrapper class for the etree element at the root of the supplied JUnitXML file.
    """

    result_path = testdir.tmpdir.join('junit.xml')
    config_path = testdir.tmpdir.join('conf.conf')
    with open(str(config_path), 'w') as f:
        f.write(config)

    result = testdir.runpytest("--junitxml={}".format(result_path), "-c={}".format(config_path), *runpytest_args)

    assert result.ret == exit_code_exp

    junit_xml_doc = JunitXml(str(result_path))

    return junit_xml_doc


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
    """An Python function decorated with a single pytest mark with the following named formatters:

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
    """An Python function decorated with the required 'test_id' and 'jira' marks along with the following named
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
def sleepy_test_function():
    """An Python function that sleeps for a period of time with the following named formatters:

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
