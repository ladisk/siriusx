"""
Unit tests for the get_sample_rate() and set_sample_rate() methods in SiriusX.

These tests validate the sample rate handling logic, including getting and
setting sample rates, device property interaction, and state management.
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from siriusx import SiriusX


class TestGetSampleRate:
    """Tests for SiriusX.get_sample_rate() method."""

    @patch('siriusx.core.opendaq.Instance')
    def test_get_sample_rate_returns_device_property(self, mock_instance_class):
        """
        Validates: get_sample_rate() retrieves sample rate from device property.

        Synthetic Input:
            - mock_device.get_property_value("SampleRate") returns 1000.0

        Prediction:
            - get_sample_rate() returns 1000.0
            - get_property_value() called with "SampleRate"
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_device.get_property_value.return_value = 1000.0
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.device = mock_device

        # Act
        result = sx.get_sample_rate()

        # Assert
        assert result == 1000.0
        mock_device.get_property_value.assert_called_once_with("SampleRate")

    @patch('siriusx.core.opendaq.Instance')
    def test_get_sample_rate_updates_self_sample_rate(self, mock_instance_class):
        """
        Validates: get_sample_rate() updates self.sample_rate attribute.

        Synthetic Input:
            - mock_device.get_property_value("SampleRate") returns 2000.0
            - self.sample_rate initially None

        Prediction:
            - After calling get_sample_rate(), self.sample_rate equals 2000.0
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_device.get_property_value.return_value = 2000.0
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.device = mock_device
        assert sx.sample_rate is None  # Verify initial state

        # Act
        sx.get_sample_rate()

        # Assert
        assert sx.sample_rate == 2000.0


class TestSetSampleRate:
    """Tests for SiriusX.set_sample_rate() method."""

    @patch('siriusx.core.opendaq.Instance')
    def test_set_sample_rate_sets_and_returns_actual(self, mock_instance_class):
        """
        Validates: set_sample_rate() sets device property and returns actual rate.

        Synthetic Input:
            - Request rate 1000
            - mock_device.get_property_value("SampleRate") returns 1000.0

        Prediction:
            - set_property_value() called with ("SampleRate", 1000)
            - Returns 1000.0
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_device.get_property_value.return_value = 1000.0
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.device = mock_device
        requested_rate = 1000

        # Act
        result = sx.set_sample_rate(requested_rate)

        # Assert
        mock_device.set_property_value.assert_called_once_with("SampleRate", 1000)
        assert result == 1000.0

    @patch('siriusx.core.opendaq.Instance')
    def test_set_sample_rate_device_adjusts_rate(self, mock_instance_class):
        """
        Validates: set_sample_rate() handles device adjustment of requested rate.

        Synthetic Input:
            - Request rate 1234
            - mock_device.get_property_value("SampleRate") returns 1000.0 (device adjusted)

        Prediction:
            - set_property_value() called with ("SampleRate", 1234)
            - Returns 1000.0 (the adjusted value)
            - self.sample_rate equals 1000.0
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_device.get_property_value.return_value = 1000.0  # Device adjusted to 1000
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.device = mock_device
        requested_rate = 1234

        # Act
        result = sx.set_sample_rate(requested_rate)

        # Assert
        mock_device.set_property_value.assert_called_once_with("SampleRate", 1234)
        assert result == 1000.0
        assert sx.sample_rate == 1000.0
