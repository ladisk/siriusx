"""
Unit tests for error handling in SiriusX when methods are called in wrong states.

These tests validate that appropriate exceptions are raised when methods are
called before required initialization steps (e.g., calling methods before
connecting, or reading before creating reader).
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from siriusx import SiriusX


class TestNotConnectedScenarios:
    """Tests for methods called when device is not connected."""

    @patch('siriusx.core.opendaq.Instance')
    def test_get_sample_rate_when_not_connected(self, mock_instance_class):
        """
        Validates: get_sample_rate() raises AttributeError when device is None.

        Synthetic Input:
            - SiriusX instance created but connect() never called
            - self.device is None

        Prediction:
            - Raises AttributeError when trying to call device.get_property_value()
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        # Note: NOT calling sx.connect()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.get_sample_rate()

    @patch('siriusx.core.opendaq.Instance')
    def test_set_sample_rate_when_not_connected(self, mock_instance_class):
        """
        Validates: set_sample_rate() raises AttributeError when device is None.

        Synthetic Input:
            - SiriusX instance created but connect() never called
            - self.device is None
            - Attempting to set sample rate to 1000 Hz

        Prediction:
            - Raises AttributeError when trying to call device.set_property_value()
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        # Note: NOT calling sx.connect()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.set_sample_rate(1000)

    @patch('siriusx.core.opendaq.Instance')
    def test_get_available_channels_when_not_connected(self, mock_instance_class):
        """
        Validates: get_available_channels() raises AttributeError when device is None.

        Synthetic Input:
            - SiriusX instance created but connect() never called
            - self.device is None

        Prediction:
            - Raises AttributeError when trying to access device.channels_recursive
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        # Note: NOT calling sx.connect()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.get_available_channels()

    @patch('siriusx.core.opendaq.Instance')
    def test_get_available_ai_signals_when_not_connected(self, mock_instance_class):
        """
        Validates: get_available_ai_signals() raises AttributeError when device is None.

        Synthetic Input:
            - SiriusX instance created but connect() never called
            - self.device is None

        Prediction:
            - Raises AttributeError when trying to access device.signals_recursive
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        # Note: NOT calling sx.connect()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.get_available_ai_signals()

    @patch('siriusx.core.opendaq.Instance')
    def test_configure_channels_when_not_connected(self, mock_instance_class):
        """
        Validates: configure_channels() raises AttributeError when device is None.

        Synthetic Input:
            - SiriusX instance created but connect() never called
            - self.device is None
            - Channel settings provided for channel 0

        Prediction:
            - Raises AttributeError when trying to access device.channels_recursive
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        # Note: NOT calling sx.connect()

        channel_settings = {
            0: {
                'Name': 'test_ch',
                'Measurement': 'Voltage',
                'Range': '10',
                'HPFilter': 'DC',
                'Sensitivity': 1.0,
                'Sensitivity Unit': 'V/V',
                'Unit': 'V',
            }
        }

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.configure_channels(channel_settings)


class TestReaderNotCreatedScenarios:
    """Tests for methods called when multi_reader is not created."""

    @patch('siriusx.core.opendaq.Instance')
    def test_read_raw_when_reader_not_created(self, mock_instance_class):
        """
        Validates: read_raw() raises AttributeError when multi_reader is None.

        Synthetic Input:
            - SiriusX instance with connected device
            - create_reader() was never called
            - self.multi_reader is None

        Prediction:
            - Raises AttributeError when trying to call multi_reader.read()
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_instance.add_device.return_value = mock_device
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.connect("daq.sirius://192.168.1.100")
        # Note: NOT calling sx.create_reader()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.read_raw(sample_count=100, timeout=1.0)

    @patch('siriusx.core.opendaq.Instance')
    def test_read_processed_when_reader_not_created(self, mock_instance_class):
        """
        Validates: read_processed() raises AttributeError when multi_reader is None.

        Synthetic Input:
            - SiriusX instance with connected device
            - create_reader() was never called
            - self.multi_reader is None

        Prediction:
            - Raises AttributeError when trying to call multi_reader.read()
              via read_raw() internally
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_instance.add_device.return_value = mock_device
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.connect("daq.sirius://192.168.1.100")
        # Configure channels so channel_settings exists
        sx.channel_settings = {
            0: {
                'Sensitivity': 100.0,
                'Sensitivity Unit': 'mV/g',
                'Unit': 'g',
            }
        }
        # Note: NOT calling sx.create_reader()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.read_processed(sample_count=100, timeout=1.0)

    @patch('siriusx.core.opendaq.Instance')
    def test_available_samples_when_reader_not_created(self, mock_instance_class):
        """
        Validates: available_samples() raises AttributeError when multi_reader is None.

        Synthetic Input:
            - SiriusX instance with connected device
            - create_reader() was never called
            - self.multi_reader is None

        Prediction:
            - Raises AttributeError when trying to access multi_reader.available_count
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_instance.add_device.return_value = mock_device
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.connect("daq.sirius://192.168.1.100")
        # Note: NOT calling sx.create_reader()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.available_samples()

    @patch('siriusx.core.opendaq.Instance')
    def test_start_reader_when_reader_not_created(self, mock_instance_class):
        """
        Validates: start_reader() raises AttributeError when multi_reader is None.

        Synthetic Input:
            - SiriusX instance with connected device
            - create_reader() was never called
            - self.multi_reader is None

        Prediction:
            - Raises AttributeError when trying to call multi_reader.read()
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_instance.add_device.return_value = mock_device
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.connect("daq.sirius://192.168.1.100")
        # Note: NOT calling sx.create_reader()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.start_reader()


class TestChannelSettingsNotConfigured:
    """Tests for methods called when channel_settings is not configured."""

    @patch('siriusx.core.opendaq.MultiReader')
    @patch('siriusx.core.opendaq.Instance')
    def test_read_processed_when_channel_settings_not_set(
        self, mock_instance_class, mock_multi_reader_class
    ):
        """
        Validates: read_processed() raises AttributeError when channel_settings not set.

        Synthetic Input:
            - SiriusX instance with connected device
            - Reader created and returns data
            - configure_channels() was never called
            - self.channel_settings does not exist

        Prediction:
            - Raises AttributeError when trying to access self.channel_settings.keys()
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_instance.add_device.return_value = mock_device
        mock_instance_class.return_value = mock_instance

        mock_reader = Mock()
        mock_reader.read.return_value = np.array([[1.0, 2.0], [3.0, 4.0]])
        mock_multi_reader_class.return_value = mock_reader

        sx = SiriusX()
        sx.connect("daq.sirius://192.168.1.100")
        sx.selected_signals = [Mock(), Mock()]  # Fake signals
        sx.create_reader()
        # Note: NOT calling sx.configure_channels()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.read_processed(sample_count=100, timeout=1.0)

    @patch('siriusx.core.opendaq.MultiReader')
    @patch('siriusx.core.opendaq.Instance')
    def test_acquire_processed_when_channel_settings_not_set(
        self, mock_instance_class, mock_multi_reader_class
    ):
        """
        Validates: acquire_processed() raises AttributeError when channel_settings not set.

        Synthetic Input:
            - SiriusX instance with connected device
            - Sample rate is 1000 Hz
            - configure_channels() was never called
            - self.channel_settings does not exist

        Prediction:
            - Raises AttributeError when trying to access self.channel_settings
              during sensitivity application
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_device.get_property_value.return_value = 1000.0
        mock_instance.add_device.return_value = mock_device
        mock_instance_class.return_value = mock_instance

        mock_reader = Mock()
        mock_reader.read.return_value = np.array([[1.0, 2.0]])
        mock_multi_reader_class.return_value = mock_reader

        sx = SiriusX()
        sx.connect("daq.sirius://192.168.1.100")
        sx.selected_signals = [Mock()]  # Fake signal
        # Note: NOT calling sx.configure_channels()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.acquire_processed(acqusition_time=1.0)

    @patch('siriusx.core.opendaq.Instance')
    def test_create_reader_when_selected_signals_not_set(self, mock_instance_class):
        """
        Validates: create_reader() raises AttributeError when selected_signals not set.

        Synthetic Input:
            - SiriusX instance with connected device
            - configure_channels() was never called
            - self.selected_signals does not exist

        Prediction:
            - Raises AttributeError when trying to access self.selected_signals
              in MultiReader constructor
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_instance.add_device.return_value = mock_device
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.connect("daq.sirius://192.168.1.100")
        # Note: NOT calling sx.configure_channels()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.create_reader()


class TestApplySensitivityWithoutChannelSettings:
    """Tests for _apply_sensitivity() called without channel_settings."""

    @patch('siriusx.core.opendaq.Instance')
    def test_apply_sensitivity_when_channel_settings_not_set(self, mock_instance_class):
        """
        Validates: _apply_sensitivity() raises AttributeError when channel_settings not set.

        Synthetic Input:
            - SiriusX instance (may or may not be connected)
            - configure_channels() was never called
            - self.channel_settings does not exist
            - Attempting to apply sensitivity for channel 0

        Prediction:
            - Raises AttributeError when trying to access self.channel_settings[ch_num]
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        # Note: NOT calling sx.configure_channels()

        signal = np.array([1.0, 2.0, 3.0])

        # Act & Assert
        with pytest.raises(AttributeError):
            sx._apply_sensitivity(ch_num=0, signal=signal)

    @patch('siriusx.core.opendaq.Instance')
    def test_apply_sensitivity_with_invalid_channel_number(self, mock_instance_class):
        """
        Validates: _apply_sensitivity() raises KeyError for invalid channel number.

        Synthetic Input:
            - SiriusX instance with channel_settings configured
            - channel_settings only has channel 0
            - Attempting to apply sensitivity for channel 1 (not configured)

        Prediction:
            - Raises KeyError when trying to access self.channel_settings[1]
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.channel_settings = {
            0: {
                'Sensitivity': 100.0,
                'Sensitivity Unit': 'mV/g',
                'Unit': 'g',
            }
        }
        # Note: Only channel 0 is configured

        signal = np.array([1.0, 2.0, 3.0])

        # Act & Assert
        with pytest.raises(KeyError):
            sx._apply_sensitivity(ch_num=1, signal=signal)


class TestSequentialStateErrors:
    """Tests for operations performed in wrong sequence."""

    @patch('siriusx.core.opendaq.Instance')
    def test_acquire_raw_when_channels_not_configured(self, mock_instance_class):
        """
        Validates: acquire_raw() raises AttributeError when channels not configured.

        Synthetic Input:
            - SiriusX instance with connected device
            - configure_channels() was never called
            - self.selected_signals does not exist
            - Attempting to acquire 100 samples

        Prediction:
            - Raises AttributeError in create_reader() when trying to access
              self.selected_signals
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_instance.add_device.return_value = mock_device
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.connect("daq.sirius://192.168.1.100")
        # Note: NOT calling sx.configure_channels()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.acquire_raw(sample_count=100, timeout=1.0)

    @patch('siriusx.core.opendaq.MultiReader')
    @patch('siriusx.core.opendaq.Instance')
    def test_acquire_processed_when_device_not_connected(
        self, mock_instance_class, mock_multi_reader_class
    ):
        """
        Validates: acquire_processed() raises AttributeError when device not connected.

        Synthetic Input:
            - SiriusX instance created but connect() never called
            - self.device is None
            - Attempting to acquire processed data

        Prediction:
            - Raises AttributeError when trying to call device.get_property_value()
              in get_sample_rate()
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        # Note: NOT calling sx.connect()

        # Act & Assert
        with pytest.raises(AttributeError):
            sx.acquire_processed(acqusition_time=1.0)
