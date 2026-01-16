"""
Unit tests for the connect() method in SiriusX.

These tests validate the connection handling logic, including successful
connections, error handling, and state management.
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from siriusx import SiriusX


class TestConnect:
    """Tests for SiriusX.connect() method."""

    @patch('siriusx.core.opendaq.Instance')
    def test_connect_success(self, mock_instance_class):
        """
        Validates: Successful connection returns True and sets device attributes.

        Synthetic Input:
            - mock_instance.add_device() returns a mock device object
            - connection_string: "daq.sirius://192.168.1.100"

        Prediction:
            - Returns True
            - self.connected is set to True
            - self.device is set to the mock device object
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_instance.add_device.return_value = mock_device
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        connection_string = "daq.sirius://192.168.1.100"

        # Act
        result = sx.connect(connection_string)

        # Assert
        assert result is True
        assert sx.connected is True
        assert sx.device is mock_device

    @patch('siriusx.core.opendaq.Instance')
    def test_connect_failure(self, mock_instance_class):
        """
        Validates: Failed connection returns False and sets connected to False.

        Synthetic Input:
            - mock_instance.add_device() raises RuntimeError
            - connection_string: "daq.sirius://invalid.address"

        Prediction:
            - Returns False
            - self.connected is set to False
            - self.device remains None
        """
        # Arrange
        mock_instance = Mock()
        mock_instance.add_device.side_effect = RuntimeError("Connection failed")
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        connection_string = "daq.sirius://invalid.address"

        # Act
        result = sx.connect(connection_string)

        # Assert
        assert result is False
        assert sx.connected is False
        assert sx.device is None

    @patch('siriusx.core.opendaq.Instance')
    def test_connect_failure_prints_error(self, mock_instance_class, capsys):
        """
        Validates: Error message is printed when connection fails.

        Synthetic Input:
            - mock_instance.add_device() raises ValueError("Device not found")
            - connection_string: "daq.sirius://192.168.1.999"

        Prediction:
            - Prints "Error connecting to device: Device not found" to stdout
            - Returns False
        """
        # Arrange
        mock_instance = Mock()
        error_message = "Device not found"
        mock_instance.add_device.side_effect = ValueError(error_message)
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        connection_string = "daq.sirius://192.168.1.999"

        # Act
        result = sx.connect(connection_string)

        # Assert
        captured = capsys.readouterr()
        assert "Error connecting to device:" in captured.out
        assert error_message in captured.out
        assert result is False

    @patch('siriusx.core.opendaq.Instance')
    def test_connect_passes_connection_string(self, mock_instance_class):
        """
        Validates: Connection string is passed correctly to add_device().

        Synthetic Input:
            - connection_string: "daq.sirius://192.168.1.50"
            - mock_instance.add_device() is configured to track calls

        Prediction:
            - mock_instance.add_device() is called once with the exact
              connection string "daq.sirius://192.168.1.50"
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_instance.add_device.return_value = mock_device
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        connection_string = "daq.sirius://192.168.1.50"

        # Act
        sx.connect(connection_string)

        # Assert
        mock_instance.add_device.assert_called_once_with(connection_string)
