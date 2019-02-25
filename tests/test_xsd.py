# -*- coding: utf-8 -*-

"""Test cases for the 'get_xsd' utility function for retrieving the XSD for the project."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import absolute_import
from lxml import etree
# noinspection PyProtectedMember
# noinspection PyPackageRequirements
from zigzag.xml_parsing_facade import XmlParsingFacade
from tests.conftest import run_and_parse


# ======================================================================================================================
# Tests
# ======================================================================================================================
def test_happy_path_asc(testdir, properly_decorated_test_function, mocker, simple_test_config):
    """Verify that 'get_xsd' returns an XSD stream that can be used to validate JUnitXML."""

    # Mock
    zz = mocker.MagicMock()
    xmlpf = XmlParsingFacade(zz)

    # Setup
    testdir.makepyfile(properly_decorated_test_function.format(test_name='test_happy_path',
                                                               test_id='123e4567-e89b-12d3-a456-426655440000',
                                                               jira_id='ASC-123'))

    args = ["--pytest-zigzag-config", simple_test_config]
    xml_doc = run_and_parse(testdir, 0, args)[0].xml_doc

    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd()))

    # Test
    xmlschema.assertValid(xml_doc)


def test_happy_path_mk8s(testdir, properly_decorated_test_function, mocker, mk8s_test_config):
    """Verify that 'get_xsd' returns an XSD stream that can be used to validate JUnitXML when configured with mk8s."""

    # Mock
    zz = mocker.MagicMock()
    xmlpf = XmlParsingFacade(zz)

    # Setup
    testdir.makepyfile(properly_decorated_test_function.format(test_name='test_happy_path',
                                                               test_id='123e4567-e89b-12d3-a456-426655440000',
                                                               jira_id='ASC-123'))

    args = ["--pytest-zigzag-config", mk8s_test_config]
    xml_doc = run_and_parse(testdir, 0, args)[0].xml_doc
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd()))

    # Test
    xmlschema.assertValid(xml_doc)


def test_multiple_jira_references(testdir, mocker, simple_test_config):
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

    args = ["--pytest-zigzag-config", simple_test_config]
    xml_doc = run_and_parse(testdir, 0, args)[0].xml_doc
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd()))

    # Test
    xmlschema.assertValid(xml_doc)


def test_multiple_jira_references_mk8s(testdir, mocker, mk8s_test_config):
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

    args = ["--pytest-zigzag-config", mk8s_test_config]
    xml_doc = run_and_parse(testdir, 0, args)[0].xml_doc
    # noinspection PyProtectedMember
    xmlschema = etree.XMLSchema(etree.parse(xmlpf._get_xsd()))

    # Test
    xmlschema.assertValid(xml_doc)
