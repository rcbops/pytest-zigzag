# -*- coding: utf-8 -*-


from pytest_zigzag import ZZ_WARN_MESSAGE

# ======================================================================================================================
# Tests
# ======================================================================================================================


def test_zigzag_happy_path(testdir, single_decorated_test_function, mocker):
    """Verify that zigzag can be called from inside pytest"""

    # Setup
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'
    project_id = '12345'
    env_vars = {'QTEST_API_TOKEN': 'validtoken'}
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    result_path = testdir.tmpdir.join('junit.xml')

    # mock
    mocker.patch('zigzag.zigzag.ZigZag.parse', return_value=None)
    mocker.patch('zigzag.zigzag.ZigZag.upload_test_results')
    mocker.patch.dict('os.environ', env_vars)

    result = testdir.runpytest(
        "--junitxml={}".format(result_path),
        "--ci-environment=mk8s",
        "--zigzag",
        "--qtest-project-id={}".format(project_id))

    # Test
    assert 'ZigZag upload was successful!' in result.outlines


def test_zigzag_no_api_token(testdir, single_decorated_test_function, mocker):
    """Verify that zigzag will tell the user that there is no API token"""

    # Setup
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'
    project_id = '12345'
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    result_path = testdir.tmpdir.join('junit.xml')

    # mock
    mocker.patch('zigzag.zigzag.ZigZag.parse', return_value=None)
    mocker.patch('zigzag.zigzag.ZigZag.upload_test_results')

    result = testdir.runpytest(
        "--junitxml={}".format(result_path),
        "--ci-environment=mk8s",
        "--zigzag",
        "--qtest-project-id={}".format(project_id))

    # Test
    assert 'ZigZag upload was successful!' not in result.outlines
    assert 'The ZigZag upload was not successful' in result.outlines
    assert "'QTEST_API_TOKEN'" in result.outlines


def test_zigzag_no_project_id(testdir, single_decorated_test_function, mocker):
    """Verify that zigzag will tell the user to supply a project-id"""

    # Setup
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'
    env_vars = {'QTEST_API_TOKEN': 'validtoken'}
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    result_path = testdir.tmpdir.join('junit.xml')

    # mock
    mocker.patch('zigzag.zigzag.ZigZag.parse', return_value=None)
    mocker.patch('zigzag.zigzag.ZigZag.upload_test_results')
    mocker.patch.dict('os.environ', env_vars)

    result = testdir.runpytest(
        "--junitxml={}".format(result_path),
        "--ci-environment=mk8s",
        "--zigzag")

    # Test
    assert any([line.strip() == ZZ_WARN_MESSAGE for line in result.outlines])


def test_no_zigzag(testdir, single_decorated_test_function, mocker):
    """Verify zigzag does not run if we do no pass the --zigzag option"""

    # Setup
    mark_type_exp = 'test_id'
    test_id_exp = '123e4567-e89b-12d3-a456-426655440000'
    test_name_exp = 'test_uuid'
    project_id = '12345'
    env_vars = {'QTEST_API_TOKEN': 'validtoken'}
    testdir.makepyfile(single_decorated_test_function.format(mark_type=mark_type_exp,
                                                             mark_arg=test_id_exp,
                                                             test_name=test_name_exp))
    result_path = testdir.tmpdir.join('junit.xml')

    # mock
    mocker.patch.dict('os.environ', env_vars)

    result = testdir.runpytest(
        "--junitxml={}".format(result_path),
        "--ci-environment=mk8s",
        "--qtest-project-id={}".format(project_id))

    # Test
    assert any([line.strip() == ZZ_WARN_MESSAGE for line in result.outlines])
