"""
Unit tests for channel configuration methods in SiriusX.

These tests validate get_available_channels(), _configure_channel(),
and configure_channels() logic including property setting and signal selection.
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, call

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from siriusx import SiriusX


class TestGetAvailableChannels:
    """Tests for SiriusX.get_available_channels() method."""

    @patch('siriusx.core.opendaq.Instance')
    def test_get_available_channels_returns_list(self, mock_instance_class):
        """
        Validates: get_available_channels() returns list from device.channels_recursive.

        Synthetic Input:
            - mock_device.channels_recursive is an iterable with 2 mock channels

        Prediction:
            - Returns a list containing both mock channels
            - Length of returned list is 2
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_chan1 = Mock(name="AI 1")
        mock_chan2 = Mock(name="AI 2")
        mock_device.channels_recursive = [mock_chan1, mock_chan2]
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.device = mock_device

        # Act
        result = sx.get_available_channels()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] is mock_chan1
        assert result[1] is mock_chan2

    @patch('siriusx.core.opendaq.Instance')
    def test_get_available_channels_caches_to_self(self, mock_instance_class):
        """
        Validates: get_available_channels() stores result in self.channels.

        Synthetic Input:
            - mock_device.channels_recursive returns [mock_chan]
            - self.channels is initially not set

        Prediction:
            - After call, self.channels equals the returned list
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_chan = Mock(name="AI 1")
        mock_device.channels_recursive = [mock_chan]
        mock_instance_class.return_value = mock_instance

        sx = SiriusX()
        sx.device = mock_device
        assert not hasattr(sx, 'channels') or sx.channels is None

        # Act
        result = sx.get_available_channels()

        # Assert
        assert sx.channels == result
        assert sx.channels == [mock_chan]


class TestConfigureChannel:
    """Tests for SiriusX._configure_channel() method."""

    @patch('siriusx.core.opendaq.Instance')
    def test_configure_channel_iepe_settings(self, mock_instance_class):
        """
        Validates: _configure_channel() applies IEPE configuration correctly.

        Synthetic Input:
            - Mock channel with Amplifier function block
            - Amplifier has properties:
                - Measurement: selection_values=['Voltage', 'IEPE'], current=0
                - Range: selection_values=['200', '1000', '5000', '10000'], current=0
                - HPFilter: selection_values=['DC', 'AC 0.1Hz', 'AC 1Hz'], current=0
                - Excitation: selection_values=[2.0, 4.0, 6.0], current=0
            - Settings: {'Measurement': 'IEPE', 'Range': '10000', 'HPFilter': 'AC 1Hz', 'Excitation': 4.0}

        Prediction:
            - Measurement.value set to 1 (index of 'IEPE')
            - Range.value set to 3 (index of '10000')
            - HPFilter.value set to 2 (index of 'AC 1Hz')
            - Excitation.value set to 1 (index of 4.0)
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        # Create mock properties
        prop_measurement = Mock()
        prop_measurement.name = 'Measurement'
        prop_measurement.selection_values = ['Voltage', 'IEPE']
        prop_measurement.value = 0

        prop_range = Mock()
        prop_range.name = 'Range'
        prop_range.selection_values = ['200', '1000', '5000', '10000']
        prop_range.value = 0

        prop_hpfilter = Mock()
        prop_hpfilter.name = 'HPFilter'
        prop_hpfilter.selection_values = ['DC', 'AC 0.1Hz', 'AC 1Hz']
        prop_hpfilter.value = 0

        prop_excitation = Mock()
        prop_excitation.name = 'Excitation'
        prop_excitation.selection_values = [2.0, 4.0, 6.0]
        prop_excitation.value = 0

        # Create mock amplifier function block
        mock_amplifier = Mock()
        mock_amplifier.visible_properties = [prop_measurement, prop_range, prop_hpfilter, prop_excitation]

        # Create mock channel
        mock_channel = Mock()
        mock_channel.name = 'AI 1'
        mock_channel.get_function_blocks.return_value = [mock_amplifier]

        # Create mock device
        mock_device = Mock()
        mock_device.channels_recursive = [mock_channel]

        sx = SiriusX()
        sx.device = mock_device

        settings = {
            'Name': 'acc_X',
            'Measurement': 'IEPE',
            'Range': '10000',
            'HPFilter': 'AC 1Hz',
            'Excitation': 4.0,
        }

        # Act
        sx._configure_channel(0, settings)

        # Assert
        assert prop_measurement.value == 1  # index of 'IEPE'
        assert prop_range.value == 3        # index of '10000'
        assert prop_hpfilter.value == 2     # index of 'AC 1Hz'
        assert prop_excitation.value == 1   # index of 4.0

    @patch('siriusx.core.opendaq.Instance')
    def test_configure_channel_voltage_settings(self, mock_instance_class):
        """
        Validates: _configure_channel() applies Voltage configuration correctly.

        Synthetic Input:
            - Mock channel with Amplifier function block
            - Amplifier has properties:
                - Measurement: selection_values=['Voltage', 'IEPE'], current=1
                - Range: selection_values=['0.2', '1', '5', '10'], current=0
                - HPFilter: selection_values=['DC', 'AC 0.1Hz', 'AC 1Hz'], current=2
            - Settings: {'Measurement': 'Voltage', 'Range': '10', 'HPFilter': 'DC'}

        Prediction:
            - Measurement.value set to 0 (index of 'Voltage')
            - Range.value set to 3 (index of '10')
            - HPFilter.value set to 0 (index of 'DC')
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        prop_measurement = Mock()
        prop_measurement.name = 'Measurement'
        prop_measurement.selection_values = ['Voltage', 'IEPE']
        prop_measurement.value = 1

        prop_range = Mock()
        prop_range.name = 'Range'
        prop_range.selection_values = ['0.2', '1', '5', '10']
        prop_range.value = 0

        prop_hpfilter = Mock()
        prop_hpfilter.name = 'HPFilter'
        prop_hpfilter.selection_values = ['DC', 'AC 0.1Hz', 'AC 1Hz']
        prop_hpfilter.value = 2

        mock_amplifier = Mock()
        mock_amplifier.visible_properties = [prop_measurement, prop_range, prop_hpfilter]

        mock_channel = Mock()
        mock_channel.name = 'AI 1'
        mock_channel.get_function_blocks.return_value = [mock_amplifier]

        mock_device = Mock()
        mock_device.channels_recursive = [mock_channel]

        sx = SiriusX()
        sx.device = mock_device

        settings = {
            'Name': 'vol_1',
            'Measurement': 'Voltage',
            'Range': '10',
            'HPFilter': 'DC',
        }

        # Act
        sx._configure_channel(0, settings)

        # Assert
        assert prop_measurement.value == 0  # index of 'Voltage'
        assert prop_range.value == 3        # index of '10'
        assert prop_hpfilter.value == 0     # index of 'DC'

    @patch('siriusx.core.opendaq.Instance')
    def test_configure_channel_invalid_setting_prints_warning(self, mock_instance_class, capsys):
        """
        Validates: _configure_channel() prints warning for invalid setting value.

        Synthetic Input:
            - Mock channel with Amplifier having Range property
            - Range.selection_values = ['200', '1000', '5000', '10000']
            - Settings: {'Range': '9999'} (invalid value)

        Prediction:
            - Warning message printed containing '9999' and 'Range'
            - No exception raised
            - Range.value unchanged (stays at 0)
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        prop_range = Mock()
        prop_range.name = 'Range'
        prop_range.selection_values = ['200', '1000', '5000', '10000']
        prop_range.value = 0

        mock_amplifier = Mock()
        mock_amplifier.visible_properties = [prop_range]

        mock_channel = Mock()
        mock_channel.name = 'AI 1'
        mock_channel.get_function_blocks.return_value = [mock_amplifier]

        mock_device = Mock()
        mock_device.channels_recursive = [mock_channel]

        sx = SiriusX()
        sx.device = mock_device

        settings = {'Range': '9999'}  # Invalid value

        # Act
        sx._configure_channel(0, settings)

        # Assert
        captured = capsys.readouterr()
        assert '9999' in captured.out
        assert 'Range' in captured.out
        assert prop_range.value == 0  # Unchanged

    @patch('siriusx.core.opendaq.Instance')
    def test_configure_channel_sets_name(self, mock_instance_class):
        """
        Validates: _configure_channel() sets channel name from settings.

        Synthetic Input:
            - Mock channel with initial name 'AI 1'
            - Settings: {'Name': 'accelerometer_x'}

        Prediction:
            - channel.name set to 'accelerometer_x'
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        mock_amplifier = Mock()
        mock_amplifier.visible_properties = []

        mock_channel = Mock()
        mock_channel.name = 'AI 1'
        mock_channel.get_function_blocks.return_value = [mock_amplifier]

        mock_device = Mock()
        mock_device.channels_recursive = [mock_channel]

        sx = SiriusX()
        sx.device = mock_device

        settings = {'Name': 'accelerometer_x'}

        # Act
        sx._configure_channel(0, settings)

        # Assert
        assert mock_channel.name == 'accelerometer_x'


class TestConfigureChannels:
    """Tests for SiriusX.configure_channels() method."""

    @patch('siriusx.core.opendaq.Instance')
    def test_configure_channels_configures_multiple(self, mock_instance_class):
        """
        Validates: configure_channels() calls _configure_channel for each entry.

        Synthetic Input:
            - channel_settings with keys 0 and 1
            - Mock device with 2 channels and 2 AI signals

        Prediction:
            - _configure_channel called twice (for channels 0 and 1)
            - Each channel's function block accessed
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        mock_amp1 = Mock()
        mock_amp1.visible_properties = []
        mock_amp2 = Mock()
        mock_amp2.visible_properties = []

        mock_chan1 = Mock()
        mock_chan1.name = 'AI 1'
        mock_chan1.get_function_blocks.return_value = [mock_amp1]

        mock_chan2 = Mock()
        mock_chan2.name = 'AI 2'
        mock_chan2.get_function_blocks.return_value = [mock_amp2]

        mock_sig1 = Mock()
        mock_sig1.name = 'AI 1'
        mock_sig2 = Mock()
        mock_sig2.name = 'AI 2'

        mock_device = Mock()
        mock_device.channels_recursive = [mock_chan1, mock_chan2]
        mock_device.signals_recursive = [mock_sig1, mock_sig2]

        sx = SiriusX()
        sx.device = mock_device

        channel_settings = {
            0: {'Name': 'ch0'},
            1: {'Name': 'ch1'},
        }

        # Act
        sx.configure_channels(channel_settings)

        # Assert
        mock_chan1.get_function_blocks.assert_called()
        mock_chan2.get_function_blocks.assert_called()
        assert mock_chan1.name == 'ch0'
        assert mock_chan2.name == 'ch1'

    @patch('siriusx.core.opendaq.Instance')
    def test_configure_channels_populates_channel_settings(self, mock_instance_class):
        """
        Validates: configure_channels() stores settings in self.channel_settings.

        Synthetic Input:
            - channel_settings dict with channel 0 configuration

        Prediction:
            - self.channel_settings equals the input dict
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        mock_amp = Mock()
        mock_amp.visible_properties = []

        mock_chan = Mock()
        mock_chan.name = 'AI 1'
        mock_chan.get_function_blocks.return_value = [mock_amp]

        mock_sig = Mock()
        mock_sig.name = 'AI 1'

        mock_device = Mock()
        mock_device.channels_recursive = [mock_chan]
        mock_device.signals_recursive = [mock_sig]

        sx = SiriusX()
        sx.device = mock_device

        channel_settings = {
            0: {
                'Name': 'acc_X',
                'Measurement': 'IEPE',
                'Sensitivity': 100,
                'Sensitivity Unit': 'mV/g',
                'Unit': 'g',
            }
        }

        # Act
        sx.configure_channels(channel_settings)

        # Assert
        assert sx.channel_settings == channel_settings
        assert sx.channel_settings[0]['Name'] == 'acc_X'
        assert sx.channel_settings[0]['Sensitivity'] == 100

    @patch('siriusx.core.opendaq.Instance')
    def test_configure_channels_populates_selected_signals(self, mock_instance_class):
        """
        Validates: configure_channels() populates self.selected_signals correctly.

        Synthetic Input:
            - channel_settings with channels 0 and 2 (not 1)
            - device.signals_recursive has 3 AI signals

        Prediction:
            - self.selected_channels equals [0, 2]
            - self.selected_signals contains signals at indices 0 and 2
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        mock_amp = Mock()
        mock_amp.visible_properties = []

        mock_chan0 = Mock()
        mock_chan0.name = 'AI 1'
        mock_chan0.get_function_blocks.return_value = [mock_amp]
        mock_chan1 = Mock()
        mock_chan1.name = 'AI 2'
        mock_chan1.get_function_blocks.return_value = [mock_amp]
        mock_chan2 = Mock()
        mock_chan2.name = 'AI 3'
        mock_chan2.get_function_blocks.return_value = [mock_amp]

        mock_sig0 = Mock()
        mock_sig0.name = 'AI 1'
        mock_sig1 = Mock()
        mock_sig1.name = 'AI 2'
        mock_sig2 = Mock()
        mock_sig2.name = 'AI 3'

        mock_device = Mock()
        mock_device.channels_recursive = [mock_chan0, mock_chan1, mock_chan2]
        mock_device.signals_recursive = [mock_sig0, mock_sig1, mock_sig2]

        sx = SiriusX()
        sx.device = mock_device

        channel_settings = {
            0: {'Name': 'ch0'},
            2: {'Name': 'ch2'},
        }

        # Act
        sx.configure_channels(channel_settings)

        # Assert
        assert sx.selected_channels == [0, 2]
        assert len(sx.selected_signals) == 2
        assert sx.selected_signals[0] is mock_sig0
        assert sx.selected_signals[1] is mock_sig2
