#
# Copyright (c) 2023 Project CHIP Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# flake8: noqa
# Ignore flake8 check for this file
from typing import Type
from unittest import mock

import pytest

from app.chip_tool.chip_tool import ChipTool
from app.models.test_suite_execution import TestSuiteExecution
from app.schemas import PICS
from app.test_engine.logger import test_engine_logger
from app.tests.utils.test_pics_data import create_random_pics
from test_collections.sdk_tests.support.python_testing.models.test_suite import (
    PythonTestSuite,
    SuiteType,
)


def test_python_suite_class_factory_name() -> None:
    """Test that test suite name is set."""
    name = "AnotherTestSuite"

    # Create a subclass of PythonTestSuite
    suite_class: Type[PythonTestSuite] = PythonTestSuite.class_factory(
        suite_type=SuiteType.AUTOMATED, name=name, python_test_version="version"
    )

    assert suite_class.__name__ == name
    assert suite_class.public_id() == name
    assert suite_class.metadata["title"] == name
    assert suite_class.metadata["description"] == name


def test_python_test_suite_python_version() -> None:
    """Test that test suite python version is set correctly in class factory."""
    python_test_version = "best_version"
    # Create a subclass of PythonTestSuite
    suite_class: Type[PythonTestSuite] = PythonTestSuite.class_factory(
        suite_type=SuiteType.AUTOMATED,
        name="SomeSuite",
        python_test_version=python_test_version,
    )

    assert suite_class.python_test_version == python_test_version


@pytest.mark.asyncio
async def test_suite_setup_log_python_version() -> None:
    """Test that test suite python version is logged to test engine logger in setup."""
    chip_tool: ChipTool = ChipTool()

    for type in list(SuiteType):
        python_test_version = "best_version"
        # Create a subclass of PythonTestSuite
        suite_class: Type[PythonTestSuite] = PythonTestSuite.class_factory(
            suite_type=type, name="SomeSuite", python_test_version=python_test_version
        )

        suite_instance = suite_class(TestSuiteExecution())

        with mock.patch.object(
            target=test_engine_logger, attribute="info"
        ) as logger_info, mock.patch.object(
            target=chip_tool, attribute="start_container"
        ), mock.patch(
            target="test_collections.sdk_tests.support.python_testing.models.test_suite"
            ".PythonTestSuite.pics",
            new_callable=PICS,
        ):
            await suite_instance.setup()
            logger_info.assert_called()
            logger_info.assert_any_call(f"Python Test Version: {python_test_version}")


@pytest.mark.asyncio
async def test_suite_setup_without_pics() -> None:
    chip_tool: ChipTool = ChipTool()

    for type in list(SuiteType):
        python_test_version = "best_version"
        # Create a subclass of PythonTestSuite
        suite_class: Type[PythonTestSuite] = PythonTestSuite.class_factory(
            suite_type=type, name="SomeSuite", python_test_version=python_test_version
        )

        suite_instance = suite_class(TestSuiteExecution())

        with mock.patch(
            "app.chip_tool.test_suite.ChipToolSuite.setup"
        ), mock.patch.object(target=chip_tool, attribute="start_container"), mock.patch(
            target="test_collections.sdk_tests.support.python_testing.models.test_suite"
            ".PythonTestSuite.pics",
            new_callable=PICS,
        ), mock.patch.object(
            target=chip_tool, attribute="set_pics"
        ) as mock_set_pics, mock.patch.object(
            target=chip_tool, attribute="reset_pics_state"
        ) as mock_reset_pics_state:
            await suite_instance.setup()

        mock_set_pics.assert_not_called()
        mock_reset_pics_state.assert_called_once()


@pytest.mark.asyncio
async def test_suite_setup_with_pics() -> None:
    chip_tool: ChipTool = ChipTool()

    for type in list(SuiteType):
        python_test_version = "best_version"
        # Create a subclass of PythonTestSuite
        suite_class: Type[PythonTestSuite] = PythonTestSuite.class_factory(
            suite_type=type, name="SomeSuite", python_test_version=python_test_version
        )

        suite_instance = suite_class(TestSuiteExecution())

        with mock.patch(
            "app.chip_tool.test_suite.ChipToolSuite.setup"
        ), mock.patch.object(target=chip_tool, attribute="start_container"), mock.patch(
            target="test_collections.sdk_tests.support.python_testing.models.test_suite"
            ".PythonTestSuite.pics",
            new_callable=create_random_pics,
        ), mock.patch.object(
            target=chip_tool, attribute="set_pics"
        ) as mock_set_pics, mock.patch.object(
            target=chip_tool, attribute="reset_pics_state"
        ) as mock_reset_pics_state:
            await suite_instance.setup()

        mock_set_pics.assert_called_once()
        mock_reset_pics_state.assert_not_called()


@pytest.mark.asyncio
async def test_chip_tool_suite_setup() -> None:
    """Test that PythonTestSuite.setup is called when PythonChipToolsSuite.setup is called.
    We do this as PythonChipToolsSuite inherits from PythonTestSuite."""

    suite_class: Type[PythonTestSuite] = PythonTestSuite.class_factory(
        suite_type=SuiteType.AUTOMATED,
        name="SomeSuite",
        python_test_version="Some version",
    )

    suite_instance = suite_class(TestSuiteExecution())

    with mock.patch(
        "test_collections.sdk_tests.support.python_testing.models.test_suite.PythonTestSuite.setup"
    ) as python_suite_setup:
        await suite_instance.setup()
        python_suite_setup.assert_called_once()
