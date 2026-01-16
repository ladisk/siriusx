"""
Unit tests for device discovery in SiriusX.

These tests validate the list_available_devices() method which discovers
and lists available Sirius X devices on the network.
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from siriusx import SiriusX


class TestListAvailableDevices:
    """Tests for SiriusX.list_available_devices() method."""

    def test_list_available_devices_returns_list(self, mock_device_info):
        """
        Validates: list_available_devices() returns correct list format when return_list=True.

        Synthetic Input:
            - Two mock devices available: "SiriusX-1" and "SiriusX-2"
            - Device 1: name="SiriusX-1", connection_string="daq.sirius://192.168.1.100"
            - Device 2: name="SiriusX-2", connection_string="daq.sirius://192.168.1.101"
            - return_list=True

        Prediction:
            Returns list with two tuples:
            [
                ("Name:", "SiriusX-1", "Connection string:", "daq.sirius://192.168.1.100"),
                ("Name:", "SiriusX-2", "Connection string:", "daq.sirius://192.168.1.101")
            ]
        """
        # Arrange
        device_info_1 = mock_device_info(
            name="SiriusX-1",
            connection_string="daq.sirius://192.168.1.100"
        )
        device_info_2 = mock_device_info(
            name="SiriusX-2",
            connection_string="daq.sirius://192.168.1.101"
        )

        with patch('siriusx.core.opendaq.Instance') as mock_instance_class:
            mock_instance = Mock()
            mock_instance.available_devices = [device_info_1, device_info_2]
            mock_instance_class.return_value = mock_instance

            sx = SiriusX()

            # Act
            result = sx.list_available_devices(print_devices=False, return_list=True)

            # Assert
            expected = [
                ("Name:", "SiriusX-1", "Connection string:", "daq.sirius://192.168.1.100"),
                ("Name:", "SiriusX-2", "Connection string:", "daq.sirius://192.168.1.101")
            ]
            assert result == expected

    def test_list_available_devices_returns_none_by_default(self, mock_device_info):
        """
        Validates: list_available_devices() returns None when return_list=False (default).

        Synthetic Input:
            - One mock device available: "SiriusX-1"
            - Device: name="SiriusX-1", connection_string="daq.sirius://192.168.1.100"
            - return_list=False (default parameter)

        Prediction:
            Returns None (function has no explicit return when return_list=False)
        """
        # Arrange
        device_info_1 = mock_device_info(
            name="SiriusX-1",
            connection_string="daq.sirius://192.168.1.100"
        )

        with patch('siriusx.core.opendaq.Instance') as mock_instance_class:
            mock_instance = Mock()
            mock_instance.available_devices = [device_info_1]
            mock_instance_class.return_value = mock_instance

            sx = SiriusX()

            # Act
            result = sx.list_available_devices(print_devices=False, return_list=False)

            # Assert
            assert result is None

    def test_list_available_devices_empty(self):
        """
        Validates: list_available_devices() handles empty device list correctly.

        Synthetic Input:
            - No devices available (empty list)
            - return_list=True

        Prediction:
            Returns empty list []
        """
        # Arrange
        with patch('siriusx.core.opendaq.Instance') as mock_instance_class:
            mock_instance = Mock()
            mock_instance.available_devices = []
            mock_instance_class.return_value = mock_instance

            sx = SiriusX()

            # Act
            result = sx.list_available_devices(print_devices=False, return_list=True)

            # Assert
            assert result == []

    def test_list_available_devices_prints_output(self, mock_device_info, capsys):
        """
        Validates: list_available_devices() prints device info when print_devices=True.

        Synthetic Input:
            - Two mock devices available
            - Device 1: name="SiriusX-1", connection_string="daq.sirius://192.168.1.100"
            - Device 2: name="SiriusX-2", connection_string="daq.sirius://192.168.1.101"
            - print_devices=True (default)

        Prediction:
            Prints two lines to stdout:
            "Name: SiriusX-1 Connection string: daq.sirius://192.168.1.100"
            "Name: SiriusX-2 Connection string: daq.sirius://192.168.1.101"
        """
        # Arrange
        device_info_1 = mock_device_info(
            name="SiriusX-1",
            connection_string="daq.sirius://192.168.1.100"
        )
        device_info_2 = mock_device_info(
            name="SiriusX-2",
            connection_string="daq.sirius://192.168.1.101"
        )

        with patch('siriusx.core.opendaq.Instance') as mock_instance_class:
            mock_instance = Mock()
            mock_instance.available_devices = [device_info_1, device_info_2]
            mock_instance_class.return_value = mock_instance

            sx = SiriusX()

            # Act
            sx.list_available_devices(print_devices=True, return_list=False)

            # Assert
            captured = capsys.readouterr()
            assert "Name: SiriusX-1 Connection string: daq.sirius://192.168.1.100" in captured.out
            assert "Name: SiriusX-2 Connection string: daq.sirius://192.168.1.101" in captured.out
            assert captured.out.count("Name:") == 2
            assert captured.out.count("Connection string:") == 2

    def test_list_available_devices_no_print(self, mock_device_info, capsys):
        """
        Validates: list_available_devices() does not print when print_devices=False.

        Synthetic Input:
            - Two mock devices available
            - Device 1: name="SiriusX-1", connection_string="daq.sirius://192.168.1.100"
            - Device 2: name="SiriusX-2", connection_string="daq.sirius://192.168.1.101"
            - print_devices=False

        Prediction:
            No output to stdout (empty string)
        """
        # Arrange
        device_info_1 = mock_device_info(
            name="SiriusX-1",
            connection_string="daq.sirius://192.168.1.100"
        )
        device_info_2 = mock_device_info(
            name="SiriusX-2",
            connection_string="daq.sirius://192.168.1.101"
        )

        with patch('siriusx.core.opendaq.Instance') as mock_instance_class:
            mock_instance = Mock()
            mock_instance.available_devices = [device_info_1, device_info_2]
            mock_instance_class.return_value = mock_instance

            sx = SiriusX()

            # Act
            sx.list_available_devices(print_devices=False, return_list=False)

            # Assert
            captured = capsys.readouterr()
            assert captured.out == ""

    def test_list_available_devices_single_device(self, mock_device_info):
        """
        Validates: list_available_devices() handles single device correctly.

        Synthetic Input:
            - One mock device available
            - Device: name="SiriusX-Dev", connection_string="daq.sirius://10.0.0.50"
            - return_list=True
            - print_devices=False

        Prediction:
            Returns list with one tuple:
            [("Name:", "SiriusX-Dev", "Connection string:", "daq.sirius://10.0.0.50")]
        """
        # Arrange
        device_info = mock_device_info(
            name="SiriusX-Dev",
            connection_string="daq.sirius://10.0.0.50"
        )

        with patch('siriusx.core.opendaq.Instance') as mock_instance_class:
            mock_instance = Mock()
            mock_instance.available_devices = [device_info]
            mock_instance_class.return_value = mock_instance

            sx = SiriusX()

            # Act
            result = sx.list_available_devices(print_devices=False, return_list=True)

            # Assert
            expected = [
                ("Name:", "SiriusX-Dev", "Connection string:", "daq.sirius://10.0.0.50")
            ]
            assert result == expected

    def test_list_available_devices_both_print_and_return(
        self, mock_device_info, capsys
    ):
        """
        Validates: list_available_devices() can both print and return simultaneously.

        Synthetic Input:
            - One mock device available
            - Device: name="SiriusX-1", connection_string="daq.sirius://192.168.1.100"
            - print_devices=True
            - return_list=True

        Prediction:
            Returns list with one tuple AND prints device info to stdout
        """
        # Arrange
        device_info = mock_device_info(
            name="SiriusX-1",
            connection_string="daq.sirius://192.168.1.100"
        )

        with patch('siriusx.core.opendaq.Instance') as mock_instance_class:
            mock_instance = Mock()
            mock_instance.available_devices = [device_info]
            mock_instance_class.return_value = mock_instance

            sx = SiriusX()

            # Act
            result = sx.list_available_devices(print_devices=True, return_list=True)

            # Assert
            expected = [
                ("Name:", "SiriusX-1", "Connection string:", "daq.sirius://192.168.1.100")
            ]
            assert result == expected

            captured = capsys.readouterr()
            assert "Name: SiriusX-1 Connection string: daq.sirius://192.168.1.100" in captured.out
