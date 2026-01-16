"""
Unit tests for data acquisition methods in SiriusX.

These tests validate create_reader(), start_reader(), read_raw(),
read_processed(), acquire_raw(), and acquire_processed() logic.
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, call
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from siriusx import SiriusX


class TestCreateReader:
    """Tests for SiriusX.create_reader() method."""

    @patch('siriusx.core.opendaq.MultiReader')
    @patch('siriusx.core.opendaq.Instance')
    def test_create_reader_creates_multi_reader(self, mock_instance_class, mock_multireader_class):
        """
        Validates: create_reader() creates MultiReader with selected_signals.

        Synthetic Input:
            - sx.selected_signals contains [mock_sig1, mock_sig2]
            - opendaq.MultiReader is mocked

        Prediction:
            - MultiReader() called with signals=[mock_sig1, mock_sig2]
            - self.multi_reader set to the created reader instance
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        mock_reader = Mock()
        mock_multireader_class.return_value = mock_reader

        mock_sig1 = Mock()
        mock_sig1.name = 'AI 1'
        mock_sig2 = Mock()
        mock_sig2.name = 'AI 2'

        sx = SiriusX()
        sx.selected_signals = [mock_sig1, mock_sig2]

        # Act
        sx.create_reader()

        # Assert
        mock_multireader_class.assert_called_once()
        call_kwargs = mock_multireader_class.call_args[1]
        assert call_kwargs['signals'] == [mock_sig1, mock_sig2]
        assert sx.multi_reader is mock_reader

    @patch('siriusx.core.opendaq.MultiReader')
    @patch('siriusx.core.opendaq.Instance')
    def test_create_reader_sets_timeout_type(self, mock_instance_class, mock_multireader_class):
        """
        Validates: create_reader() sets timeout_type to All.

        Synthetic Input:
            - sx.selected_signals is empty list []
            - opendaq.ReadTimeoutType.All is available

        Prediction:
            - MultiReader called with timeout_type=opendaq.ReadTimeoutType.All
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        mock_reader = Mock()
        mock_multireader_class.return_value = mock_reader

        sx = SiriusX()
        sx.selected_signals = []

        # Act
        sx.create_reader()

        # Assert
        call_kwargs = mock_multireader_class.call_args[1]
        # Import opendaq to get the actual enum value
        import opendaq
        assert call_kwargs['timeout_type'] == opendaq.ReadTimeoutType.All


class TestStartReader:
    """Tests for SiriusX.start_reader() method."""

    @patch('siriusx.core.opendaq.Instance')
    def test_start_reader_calls_read_with_zero_count(self, mock_instance_class):
        """
        Validates: start_reader() calls read(count=0, timeout_ms=10).

        Synthetic Input:
            - sx.multi_reader is mock with read() method
            - read() returns empty array

        Prediction:
            - multi_reader.read() called once with count=0 and timeout_ms=10
            - Return value is discarded (no assignment)
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        mock_reader = Mock()
        mock_reader.read.return_value = np.array([])

        sx = SiriusX()
        sx.multi_reader = mock_reader

        # Act
        sx.start_reader()

        # Assert
        mock_reader.read.assert_called_once_with(count=0, timeout_ms=10)


class TestReadRaw:
    """Tests for SiriusX.read_raw() method."""

    @patch('siriusx.core.opendaq.Instance')
    def test_read_raw_returns_transposed_data(self, mock_instance_class):
        """
        Validates: read_raw() transposes data from reader.

        Synthetic Input:
            - multi_reader.read() returns shape (2, 3) array [[1, 2, 3], [4, 5, 6]]
            - sample_count=3, timeout=1.0

        Prediction:
            - reader.read() called with count=3, timeout_ms=1000
            - Output is transposed to shape (3, 2): [[1, 4], [2, 5], [3, 6]]
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        raw_data = np.array([[1, 2, 3], [4, 5, 6]])  # 2 channels, 3 samples
        mock_reader = Mock()
        mock_reader.read.return_value = raw_data

        sx = SiriusX()
        sx.multi_reader = mock_reader

        # Act
        result = sx.read_raw(sample_count=3, timeout=1.0)

        # Assert
        mock_reader.read.assert_called_once_with(count=3, timeout_ms=1000)
        expected = np.array([[1, 4], [2, 5], [3, 6]])  # Transposed
        np.testing.assert_array_equal(result, expected)
        assert result.shape == (3, 2)

    @patch('siriusx.core.opendaq.Instance')
    def test_read_raw_empty_data_returns_empty(self, mock_instance_class):
        """
        Validates: read_raw() handles empty data correctly.

        Synthetic Input:
            - multi_reader.read() returns empty array with size=0
            - sample_count=100, timeout=2.0

        Prediction:
            - Returns empty numpy array without attempting transpose
            - Result.size == 0
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        empty_data = np.array([])
        mock_reader = Mock()
        mock_reader.read.return_value = empty_data

        sx = SiriusX()
        sx.multi_reader = mock_reader

        # Act
        result = sx.read_raw(sample_count=100, timeout=2.0)

        # Assert
        assert result.size == 0
        np.testing.assert_array_equal(result, np.array([]))

    @patch('siriusx.core.opendaq.Instance')
    def test_read_raw_timeout_conversion(self, mock_instance_class):
        """
        Validates: read_raw() converts timeout from seconds to milliseconds.

        Synthetic Input:
            - timeout=2.5 seconds
            - sample_count=50

        Prediction:
            - reader.read() called with timeout_ms=2500 (2.5 * 1000)
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        mock_reader = Mock()
        mock_reader.read.return_value = np.array([[1, 2], [3, 4]])

        sx = SiriusX()
        sx.multi_reader = mock_reader

        # Act
        sx.read_raw(sample_count=50, timeout=2.5)

        # Assert
        mock_reader.read.assert_called_once_with(count=50, timeout_ms=2500)


class TestReadProcessed:
    """Tests for SiriusX.read_processed() method."""

    @patch('siriusx.core.opendaq.Instance')
    def test_read_processed_applies_sensitivity(self, mock_instance_class):
        """
        Validates: read_processed() applies sensitivity to each channel.

        Synthetic Input:
            - sx.channel_settings has channels 0 and 1
            - read_raw() returns shape (3, 2): [[100, 200], [110, 220], [120, 240]]
            - _apply_sensitivity() multiplies by 2 for testing

        Prediction:
            - _apply_sensitivity called twice (once per channel)
            - Each column processed independently
            - Result transposed back to (3, 2)
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        mock_reader = Mock()
        raw_data = np.array([[100, 200], [110, 220], [120, 240]])  # 3 samples, 2 channels
        mock_reader.read.return_value = raw_data.T  # read_raw expects transposed input

        sx = SiriusX()
        sx.multi_reader = mock_reader
        sx.channel_settings = {
            0: {'Sensitivity': 1, 'Sensitivity Unit': 'mV/g', 'Unit': 'g'},
            1: {'Sensitivity': 1, 'Sensitivity Unit': 'mV/g', 'Unit': 'g'},
        }

        # Mock _apply_sensitivity to multiply by 2 for testing
        def mock_apply_sens(ch_num, signal):
            return signal * 2

        sx._apply_sensitivity = Mock(side_effect=mock_apply_sens)

        # Act
        result = sx.read_processed(sample_count=3, timeout=1.0)

        # Assert
        assert sx._apply_sensitivity.call_count == 2
        # Check that correct signals were passed to _apply_sensitivity
        call_args_list = sx._apply_sensitivity.call_args_list
        np.testing.assert_array_equal(call_args_list[0][1]['signal'], [100, 110, 120])
        np.testing.assert_array_equal(call_args_list[1][1]['signal'], [200, 220, 240])

        # Result should be transposed and sensitivity applied (multiplied by 2)
        expected = np.array([[200, 400], [220, 440], [240, 480]])
        np.testing.assert_array_equal(result, expected)

    @patch('siriusx.core.opendaq.Instance')
    def test_read_processed_empty_returns_empty(self, mock_instance_class):
        """
        Validates: read_processed() handles empty data without processing.

        Synthetic Input:
            - read_raw() returns empty array
            - sx.channel_settings has 2 channels

        Prediction:
            - Returns empty array immediately
            - _apply_sensitivity NOT called
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        mock_reader = Mock()
        mock_reader.read.return_value = np.array([])

        sx = SiriusX()
        sx.multi_reader = mock_reader
        sx.channel_settings = {
            0: {'Sensitivity': 1, 'Sensitivity Unit': 'mV/g', 'Unit': 'g'},
            1: {'Sensitivity': 1, 'Sensitivity Unit': 'mV/g', 'Unit': 'g'},
        }
        sx._apply_sensitivity = Mock()

        # Act
        result = sx.read_processed(sample_count=100, timeout=2.0)

        # Assert
        assert result.size == 0
        sx._apply_sensitivity.assert_not_called()


class TestAcquireRaw:
    """Tests for SiriusX.acquire_raw() method."""

    @patch('siriusx.core.opendaq.MultiReader')
    @patch('siriusx.core.opendaq.Instance')
    def test_acquire_raw_creates_reader_and_reads(self, mock_instance_class, mock_multireader_class):
        """
        Validates: acquire_raw() performs full reader lifecycle.

        Synthetic Input:
            - sx.selected_signals has 1 signal
            - reader.read() returns shape (1, 5) array
            - sample_count=5, timeout=1.0

        Prediction:
            - create_reader() creates MultiReader
            - start_reader() calls read(count=0, timeout_ms=10)
            - read_raw() calls read(count=5, timeout_ms=1000)
            - stop_reader() sets multi_reader to None
            - Returns transposed data shape (5, 1)
        """
        # Arrange
        mock_instance = Mock()
        mock_instance_class.return_value = mock_instance

        raw_data = np.array([[10, 20, 30, 40, 50]])  # 1 channel, 5 samples
        mock_reader = Mock()
        mock_reader.read.return_value = raw_data
        mock_multireader_class.return_value = mock_reader

        mock_sig = Mock()
        mock_sig.name = 'AI 1'

        sx = SiriusX()
        sx.selected_signals = [mock_sig]

        # Act
        result = sx.acquire_raw(sample_count=5, timeout=1.0)

        # Assert
        # Verify reader lifecycle
        assert mock_reader.read.call_count == 2  # Once for start (count=0), once for read
        assert mock_reader.read.call_args_list[0] == call(count=0, timeout_ms=10)
        assert mock_reader.read.call_args_list[1] == call(count=5, timeout_ms=1000)

        # Verify data shape (transposed)
        assert result.shape == (5, 1)
        expected = np.array([[10], [20], [30], [40], [50]])
        np.testing.assert_array_equal(result, expected)

        # Verify cleanup
        assert sx.multi_reader is None


class TestAcquireProcessed:
    """Tests for SiriusX.acquire_processed() method."""

    @patch('siriusx.core.opendaq.MultiReader')
    @patch('siriusx.core.opendaq.Instance')
    def test_acquire_processed_returns_array(self, mock_instance_class, mock_multireader_class):
        """
        Validates: acquire_processed() returns numpy array by default.

        Synthetic Input:
            - acquisition_time=1.0 seconds
            - sample_rate=10 Hz (10 samples)
            - 2 channels with sensitivity=1
            - reader returns shape (2, 10)

        Prediction:
            - calculate sample_count = 1.0 * 10 = 10
            - acquire_raw() called with sample_count=10, timeout=2.0
            - _apply_sensitivity called for each channel
            - Returns transposed array shape (10, 2)
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_device.get_property_value.return_value = 10.0  # sample_rate
        mock_instance_class.return_value = mock_instance

        raw_data = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                             [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]])
        mock_reader = Mock()
        mock_reader.read.return_value = raw_data
        mock_multireader_class.return_value = mock_reader

        mock_sig1 = Mock()
        mock_sig1.name = 'AI 1'
        mock_sig2 = Mock()
        mock_sig2.name = 'AI 2'

        sx = SiriusX()
        sx.device = mock_device
        sx.selected_signals = [mock_sig1, mock_sig2]
        sx.channel_settings = {
            0: {'Name': 'ch0', 'Sensitivity': 10, 'Sensitivity Unit': 'mV/g', 'Unit': 'g'},
            1: {'Name': 'ch1', 'Sensitivity': 20, 'Sensitivity Unit': 'mV/g', 'Unit': 'g'},
        }

        # Mock _apply_sensitivity to divide by sensitivity
        def mock_apply_sens(ch_num, signal):
            sens = sx.channel_settings[ch_num]['Sensitivity']
            return signal / sens

        sx._apply_sensitivity = Mock(side_effect=mock_apply_sens)

        # Act
        result = sx.acquire_processed(acqusition_time=1.0, return_dict=False)

        # Assert
        assert isinstance(result, np.ndarray)
        assert result.shape == (10, 2)
        # Verify sensitivity applied: ch0 divided by 10, ch1 divided by 20
        expected = np.array([
            [0.1, 0.55],   # 1/10, 11/20
            [0.2, 0.6],    # 2/10, 12/20
            [0.3, 0.65],   # 3/10, 13/20
            [0.4, 0.7],    # 4/10, 14/20
            [0.5, 0.75],   # 5/10, 15/20
            [0.6, 0.8],    # 6/10, 16/20
            [0.7, 0.85],   # 7/10, 17/20
            [0.8, 0.9],    # 8/10, 18/20
            [0.9, 0.95],   # 9/10, 19/20
            [1.0, 1.0],    # 10/10, 20/20
        ])
        np.testing.assert_array_almost_equal(result, expected, decimal=10)

    @patch('siriusx.core.opendaq.MultiReader')
    @patch('siriusx.core.opendaq.Instance')
    def test_acquire_processed_returns_dict(self, mock_instance_class, mock_multireader_class):
        """
        Validates: acquire_processed() returns dict with channel names when return_dict=True.

        Synthetic Input:
            - acquisition_time=0.5 seconds
            - sample_rate=4 Hz (2 samples for 0.5s)
            - 2 channels: 'acc_X' and 'acc_Y'
            - return_dict=True

        Prediction:
            - Returns dict with keys: 'acc_X', 'acc_Y', 'time'
            - Each channel has 'signal' and 'unit' keys
            - time signal is np.linspace(0, 0.5, 2) = [0.0, 0.5]
        """
        # Arrange
        mock_instance = Mock()
        mock_device = Mock()
        mock_device.get_property_value.return_value = 4.0  # sample_rate
        mock_instance_class.return_value = mock_instance

        raw_data = np.array([[100, 200], [300, 400]])  # 2 channels, 2 samples
        mock_reader = Mock()
        mock_reader.read.return_value = raw_data
        mock_multireader_class.return_value = mock_reader

        mock_sig1 = Mock()
        mock_sig1.name = 'AI 1'
        mock_sig2 = Mock()
        mock_sig2.name = 'AI 2'

        sx = SiriusX()
        sx.device = mock_device
        sx.selected_signals = [mock_sig1, mock_sig2]
        sx.channel_settings = {
            0: {'Name': 'acc_X', 'Sensitivity': 100, 'Sensitivity Unit': 'mV/g', 'Unit': 'g'},
            1: {'Name': 'acc_Y', 'Sensitivity': 100, 'Sensitivity Unit': 'mV/g', 'Unit': 'm/s^2'},
        }

        # Mock _apply_sensitivity to divide by 100
        def mock_apply_sens(ch_num, signal):
            return signal / 100

        sx._apply_sensitivity = Mock(side_effect=mock_apply_sens)

        # Act
        result = sx.acquire_processed(acqusition_time=0.5, return_dict=True)

        # Assert
        assert isinstance(result, dict)
        assert 'acc_X' in result
        assert 'acc_Y' in result
        assert 'time' in result

        # Check channel data structure
        assert 'signal' in result['acc_X']
        assert 'unit' in result['acc_X']
        assert result['acc_X']['unit'] == 'g'
        np.testing.assert_array_equal(result['acc_X']['signal'], [1.0, 2.0])

        assert 'signal' in result['acc_Y']
        assert 'unit' in result['acc_Y']
        assert result['acc_Y']['unit'] == 'm/s^2'
        np.testing.assert_array_equal(result['acc_Y']['signal'], [3.0, 4.0])

        # Check time signal
        assert result['time']['unit'] == 's'
        expected_time = np.linspace(0, 0.5, 2)
        np.testing.assert_array_almost_equal(result['time']['signal'], expected_time)
