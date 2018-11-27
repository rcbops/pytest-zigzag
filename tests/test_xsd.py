# -*- coding: utf-8 -*-

"""Test cases for the 'get_xsd' utility function for retrieving the XSD for the project."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
from lxml import etree
# noinspection PyProtectedMember
from pytest_zigzag import _load_config_file
# noinspection PyPackageRequirements
from zigzag.xml_parsing_facade import XmlParsingFacade
from tests.conftest import run_and_parse
from tests.conftest import run_and_parse_with_config

# ======================================================================================================================
# Globals
# ======================================================================================================================
ASC_TEST_ENV_VARS = list(_load_config_file('asc')['environment_variables'])      # Shallow copy.
MK8S_TEST_ENV_VARS = list(_load_config_file('mk8s')['environment_variables'])      # Shallow copy.


# ======================================================================================================================
# Tests
# ======================================================================================================================
def test_happy_path_asc(testdir, properly_decorated_test_function, mocker):
    """Verify that 'get_xsd' returns an XSD stream that can be used to validate JUnitXML."""

    # Mock
    zz = mocker.MagicMock()
    xmlpf = XmlParsingFacade(zz)

    # Setup
    testdir.makepyfile(properly_decorated_test_function.format(test_name='test_happy_path',
                                                               test_id='123e4567-e89b-12d3-a456-426655440000',
                                                               jira_id='ASC-123'))

    xml_doc = run_and_parse(testdir).xml_doc
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd()))

    # Test
    xmlschema.assertValid(xml_doc)


def test_happy_path_mk8s(testdir, properly_decorated_test_function, mocker):
    """Verify that 'get_xsd' returns an XSD stream that can be used to validate JUnitXML when configured with mk8s."""

    # Mock
    zz = mocker.MagicMock()
    xmlpf = XmlParsingFacade(zz)

    # Setup
    testdir.makepyfile(properly_decorated_test_function.format(test_name='test_happy_path',
                                                               test_id='123e4567-e89b-12d3-a456-426655440000',
                                                               jira_id='ASC-123'))
    config = \
"""
[pytest]
ci-environment=mk8s
"""  # noqa

    xml_doc = run_and_parse_with_config(testdir, config).xml_doc
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd('mk8s')))

    # Test
    xmlschema.assertValid(xml_doc)


def test_multiple_jira_references(testdir, mocker):
    """Verify that 'get_xsd' returns an XSD stream when a testcase is decorated Jira mark with multiple
    arguments for the 'asc' CI environment.
    """

    # Mock
    zz = mocker.MagicMock()
    xmlpf = XmlParsingFacade(zz)

    # Setup
    testdir.makepyfile("""
                import pytest
                @pytest.mark.jira('ASC-123', 'ASC-124')
                @pytest.mark.test_id('123e4567-e89b-12d3-a456-426655440000')
                def test_xsd():
                    pass
    """)

    xml_doc = run_and_parse(testdir).xml_doc
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd()))

    # Test
    xmlschema.assertValid(xml_doc)


def test_multiple_jira_references_mk8s(testdir, mocker):
    """Verify that 'get_xsd' returns an XSD stream when a testcase is decorated Jira mark with multiple
    arguments for the 'mk8s' CI environment.
    """

    # Mock
    zz = mocker.MagicMock()
    xmlpf = XmlParsingFacade(zz)

    # Setup
    testdir.makepyfile("""
                import pytest
                @pytest.mark.jira('ASC-123', 'ASC-124')
                @pytest.mark.test_id('123e4567-e89b-12d3-a456-426655440000')
                def test_xsd():
                    pass
    """)

    xml_doc = run_and_parse(testdir).xml_doc
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd('mk8s')))

    # Test
    xmlschema.assertValid(xml_doc)


def test_missing_required_marks_asc(testdir, undecorated_test_function, mocker):
    """Verify that XSD will enforce the presence of 'test_id' and 'jira_id' properties for test cases for the 'asc'
    CI environment.
    """

    # Mock
    zz = mocker.MagicMock()
    xmlpf = XmlParsingFacade(zz)

    # Setup
    testdir.makepyfile(undecorated_test_function.format(test_name='test_typo_global'))

    xml_doc = run_and_parse(testdir).xml_doc
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd('asc')))

    # Test
    assert xmlschema.validate(xml_doc) is False


def test_missing_required_marks_mk8s(testdir, undecorated_test_function, mocker):
    """Verify that XSD will enforce the presence of 'test_id' and 'jira_id' properties for test cases  for the 'mk8s'
    CI environment.
    """

    # Mock
    zz = mocker.MagicMock()
    xmlpf = XmlParsingFacade(zz)

    # Setup
    testdir.makepyfile(undecorated_test_function.format(test_name='test_typo_global'))

    xml_doc = run_and_parse(testdir).xml_doc
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd('mk8s')))

    # Test
    assert xmlschema.validate(xml_doc) is False


def test_extra_testcase_property_asc(testdir, properly_decorated_test_function, mocker):
    """Verify that XSD will enforce the strict presence of only required test case properties for the 'asc'
    CI environment."""

    # Mock
    zz = mocker.MagicMock()
    xmlpf = XmlParsingFacade(zz)

    # Setup
    testdir.makepyfile(properly_decorated_test_function.format(test_name='test_extra_mark',
                                                               test_id='123e4567-e89b-12d3-a456-426655440000',
                                                               jira_id='ASC-123'))

    xml_doc = run_and_parse(testdir).xml_doc

    # Add another property element for the testcase.
    xml_doc.find('./testcase/properties').append(etree.Element('property',
                                                               attrib={'name': 'extra', 'value': 'fail'}))
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd('asc')))

    # Test
    assert xmlschema.validate(xml_doc) is False


def test_extra_testcase_property_mk8s(testdir, properly_decorated_test_function, mocker):
    """Verify that XSD will enforce the strict presence of only required test case properties for the 'mk8s'
    CI environment."""

    # Mock
    zz = mocker.MagicMock()
    xmlpf = XmlParsingFacade(zz)

    # Setup
    testdir.makepyfile(properly_decorated_test_function.format(test_name='test_extra_mark',
                                                               test_id='123e4567-e89b-12d3-a456-426655440000',
                                                               jira_id='ASC-123'))

    xml_doc = run_and_parse(testdir).xml_doc

    # Add another property element for the testcase.
    xml_doc.find('./testcase/properties').append(etree.Element('property',
                                                               attrib={'name': 'extra', 'value': 'fail'}))
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd('mk8s')))

    # Test
    assert xmlschema.validate(xml_doc) is False


def test_typo_property_asc(testdir, properly_decorated_test_function, mocker):
    """Verify that XSD will enforce the only certain property names are allowed for the testcase for the 'asc'
    CI environment."""

    # Mock
    zz = mocker.MagicMock()
    xmlpf = XmlParsingFacade(zz)

    # Setup
    testdir.makepyfile(properly_decorated_test_function.format(test_name='test_typo_mark',
                                                               test_id='123e4567-e89b-12d3-a456-426655440000',
                                                               jira_id='ASC-123'))

    xml_doc = run_and_parse(testdir).xml_doc

    # Add another property element for the testcase.
    xml_doc.find('./testcase/properties/property').attrib['name'] = 'wrong_test_id'
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd('asc')))

    # Test
    assert xmlschema.validate(xml_doc) is False


def test_typo_property_mk8s(testdir, properly_decorated_test_function, mocker):
    """Verify that XSD will enforce the only certain property names are allowed for the testcase for the 'mk8s'
    CI environment."""

    # Mock
    zz = mocker.MagicMock()
    xmlpf = XmlParsingFacade(zz)

    # Setup
    testdir.makepyfile(properly_decorated_test_function.format(test_name='test_typo_mark',
                                                               test_id='123e4567-e89b-12d3-a456-426655440000',
                                                               jira_id='ASC-123'))

    xml_doc = run_and_parse(testdir).xml_doc

    # Add another property element for the testcase.
    xml_doc.find('./testcase/properties/property').attrib['name'] = 'wrong_test_id'
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd()))

    # Test
    assert xmlschema.validate(xml_doc) is False
