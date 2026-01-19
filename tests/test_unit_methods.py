"""
Unit tests for list_available_channels, get_available_ai_signals, and available_samples.

Tests the untested utility methods in SiriusX class that handle channel listing,
AI signal filtering, and buffer status queries.
"""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch
from io import StringIO
import sys

from siriusx import SiriusX


# =============================================================================
# list_available_channels() Tests
# =============================================================================


def test_list_available_channels_prints_channel_info(
    mock_channel, mock_function_block, mock_property, capsys
):
    """
    Validates: list_available_channels() prints channel global_id, name, and function block properties.

    Synthetic Input:
        - Channel "AI 1" with global_id "/device/IO/AI1"
        - Function block "Amplifier" with properties:
          - Measurement: value=1, selections=['Voltage', 'IEPE']
          - Range: value=0, selections=['10', '5', '1']

    Prediction:
        Prints channel info with properly formatted properties showing
        human-readable values from selection_values.
    """
    # Arrange
    prop1 = mock_property(name="Measurement", value=1, selection_values=['Voltage', 'IEPE'])
    prop2 = mock_property(name="Range", value=0, selection_values=['10', '5', '1'])

    fb = Mock()
    fb.name = "Amplifier"
    fb.visible_properties = [prop1, prop2]

    chan = mock_channel(name="AI 1", global_id="/device/IO/AI1", function_blocks=[fb])

    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.device = Mock()
        sx.get_available_channels = Mock(return_value=[chan])

        # Act
        sx.list_available_channels()

        # Assert
        captured = capsys.readouterr()
        assert "Channel Global ID:  /device/IO/AI1" in captured.out
        assert "Channel Name     :  AI 1" in captured.out
        assert "Function Block Name:  Amplifier" in captured.out
        assert "Measurement" in captured.out
        assert "IEPE" in captured.out  # Human-readable value from selections[1]
        assert "Range" in captured.out
        assert "10" in captured.out  # Human-readable value from selections[0]


def test_list_available_channels_with_multiple_channels(
    mock_channel, mock_function_block, capsys
):
    """
    Validates: list_available_channels() prints info for all channels.

    Synthetic Input:
        - Two channels: "AI 1" and "AI 2"
        - Each has one function block with no properties

    Prediction:
        Prints both channel names and global IDs.
    """
    # Arrange
    fb1 = Mock()
    fb1.name = "Amplifier"
    fb1.visible_properties = []

    fb2 = Mock()
    fb2.name = "Amplifier"
    fb2.visible_properties = []

    chan1 = mock_channel(name="AI 1", global_id="/device/IO/AI1", function_blocks=[fb1])
    chan2 = mock_channel(name="AI 2", global_id="/device/IO/AI2", function_blocks=[fb2])

    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.device = Mock()
        sx.get_available_channels = Mock(return_value=[chan1, chan2])

        # Act
        sx.list_available_channels()

        # Assert
        captured = capsys.readouterr()
        assert "Channel Name     :  AI 1" in captured.out
        assert "Channel Name     :  AI 2" in captured.out
        assert "/device/IO/AI1" in captured.out
        assert "/device/IO/AI2" in captured.out


def test_list_available_channels_property_without_selection_values(
    mock_channel, capsys
):
    """
    Validates: list_available_channels() prints raw value when selection_values is None.

    Synthetic Input:
        - Channel with function block property:
          - Name: "Threshold"
          - Value: 42.5
          - selection_values: None (numeric property)

    Prediction:
        Prints property value as-is (42.5) instead of looking up in selection_values.
    """
    # Arrange
    prop = Mock()
    prop.name = "Threshold"
    prop.value = 42.5
    prop.selection_values = None
    prop.unit = None

    fb = Mock()
    fb.name = "Filter"
    fb.visible_properties = [prop]

    chan = mock_channel(name="AI 1", global_id="/device/IO/AI1", function_blocks=[fb])

    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.device = Mock()
        sx.get_available_channels = Mock(return_value=[chan])

        # Act
        sx.list_available_channels()

        # Assert
        captured = capsys.readouterr()
        assert "Threshold" in captured.out
        assert "42.5" in captured.out


def test_list_available_channels_property_with_unit(mock_channel, capsys):
    """
    Validates: list_available_channels() prints property unit symbol when available.

    Synthetic Input:
        - Channel with function block property:
          - Name: "Frequency"
          - Value: 1000
          - selection_values: None
          - unit.symbol: "Hz"

    Prediction:
        Prints property with unit symbol "Hz" at the end.
    """
    # Arrange
    unit = Mock()
    unit.symbol = "Hz"

    prop = Mock()
    prop.name = "Frequency"
    prop.value = 1000
    prop.selection_values = None
    prop.unit = unit

    fb = Mock()
    fb.name = "Generator"
    fb.visible_properties = [prop]

    chan = mock_channel(name="AI 1", global_id="/device/IO/AI1", function_blocks=[fb])

    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.device = Mock()
        sx.get_available_channels = Mock(return_value=[chan])

        # Act
        sx.list_available_channels()

        # Assert
        captured = capsys.readouterr()
        assert "Frequency" in captured.out
        assert "1000" in captured.out
        assert "Hz" in captured.out


def test_list_available_channels_stores_channels_attribute(mock_channel):
    """
    Validates: list_available_channels() stores channels in self.channels attribute.

    Synthetic Input:
        - get_available_channels() returns [chan1, chan2]

    Prediction:
        After calling list_available_channels(), sx.channels == [chan1, chan2].
    """
    # Arrange
    fb = Mock()
    fb.name = "Amplifier"
    fb.visible_properties = []

    chan1 = mock_channel(name="AI 1", global_id="/device/IO/AI1", function_blocks=[fb])
    chan2 = mock_channel(name="AI 2", global_id="/device/IO/AI2", function_blocks=[fb])

    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.device = Mock()
        sx.get_available_channels = Mock(return_value=[chan1, chan2])

        # Act
        sx.list_available_channels()

        # Assert
        assert sx.channels == [chan1, chan2]


# =============================================================================
# get_available_ai_signals() Tests
# =============================================================================


def test_get_available_ai_signals_returns_only_ai_signals(mock_signal):
    """
    Validates: get_available_ai_signals() returns only signals with 'AI ' in name.

    Synthetic Input:
        - device.signals_recursive contains:
          - Signal "AI 1"
          - Signal "AI 2"
          - Signal "Temperature"
          - Signal "DI 1" (digital input)

    Prediction:
        Returns list containing only "AI 1" and "AI 2" signals.
    """
    # Arrange
    sig_ai1 = mock_signal(name="AI 1", global_id="/device/sig/AI1")
    sig_ai2 = mock_signal(name="AI 2", global_id="/device/sig/AI2")
    sig_temp = mock_signal(name="Temperature", global_id="/device/sig/temp")
    sig_di = mock_signal(name="DI 1", global_id="/device/sig/DI1")

    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.device = Mock()
        sx.device.signals_recursive = [sig_ai1, sig_ai2, sig_temp, sig_di]

        # Act
        result = sx.get_available_ai_signals()

        # Assert
        assert len(result) == 2
        assert sig_ai1 in result
        assert sig_ai2 in result
        assert sig_temp not in result
        assert sig_di not in result


def test_get_available_ai_signals_filters_out_non_ai(mock_signal):
    """
    Validates: get_available_ai_signals() excludes signals without 'AI ' substring.

    Synthetic Input:
        - device.signals_recursive contains:
          - Signal "AIN1" (no space after AI)
          - Signal "MAIN" (has AI but not 'AI ')
          - Signal "Counter"

    Prediction:
        Returns empty list (no signals match 'AI ' with space).
    """
    # Arrange
    sig1 = mock_signal(name="AIN1", global_id="/device/sig/AIN1")
    sig2 = mock_signal(name="MAIN", global_id="/device/sig/MAIN")
    sig3 = mock_signal(name="Counter", global_id="/device/sig/counter")

    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.device = Mock()
        sx.device.signals_recursive = [sig1, sig2, sig3]

        # Act
        result = sx.get_available_ai_signals()

        # Assert
        assert len(result) == 0


def test_get_available_ai_signals_caches_to_attribute(mock_signal):
    """
    Validates: get_available_ai_signals() stores result in self.available_ai_signals.

    Synthetic Input:
        - device.signals_recursive contains signals "AI 1", "AI 2"

    Prediction:
        After calling get_available_ai_signals(), sx.available_ai_signals
        contains the filtered AI signals.
    """
    # Arrange
    sig_ai1 = mock_signal(name="AI 1", global_id="/device/sig/AI1")
    sig_ai2 = mock_signal(name="AI 2", global_id="/device/sig/AI2")
    sig_temp = mock_signal(name="Temperature", global_id="/device/sig/temp")

    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.device = Mock()
        sx.device.signals_recursive = [sig_ai1, sig_ai2, sig_temp]

        # Act
        result = sx.get_available_ai_signals()

        # Assert
        assert sx.available_ai_signals == result
        assert len(sx.available_ai_signals) == 2
        assert sig_ai1 in sx.available_ai_signals
        assert sig_ai2 in sx.available_ai_signals


def test_get_available_ai_signals_with_no_ai_signals(mock_signal):
    """
    Validates: get_available_ai_signals() returns empty list when no AI signals exist.

    Synthetic Input:
        - device.signals_recursive contains only non-AI signals:
          - "Temperature"
          - "DI 1"
          - "Counter"

    Prediction:
        Returns empty list.
    """
    # Arrange
    sig1 = mock_signal(name="Temperature", global_id="/device/sig/temp")
    sig2 = mock_signal(name="DI 1", global_id="/device/sig/DI1")
    sig3 = mock_signal(name="Counter", global_id="/device/sig/counter")

    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.device = Mock()
        sx.device.signals_recursive = [sig1, sig2, sig3]

        # Act
        result = sx.get_available_ai_signals()

        # Assert
        assert result == []
        assert sx.available_ai_signals == []


def test_get_available_ai_signals_case_sensitive(mock_signal):
    """
    Validates: get_available_ai_signals() is case-sensitive for 'AI ' substring.

    Synthetic Input:
        - device.signals_recursive contains:
          - "AI 1" (uppercase AI with space)
          - "ai 1" (lowercase ai with space)
          - "Ai 1" (mixed case)

    Prediction:
        Returns only "AI 1" (uppercase with space).
    """
    # Arrange
    sig1 = mock_signal(name="AI 1", global_id="/device/sig/AI1")
    sig2 = mock_signal(name="ai 1", global_id="/device/sig/ai1")
    sig3 = mock_signal(name="Ai 1", global_id="/device/sig/Ai1")

    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.device = Mock()
        sx.device.signals_recursive = [sig1, sig2, sig3]

        # Act
        result = sx.get_available_ai_signals()

        # Assert
        assert len(result) == 1
        assert sig1 in result
        assert sig2 not in result
        assert sig3 not in result


# =============================================================================
# available_samples() Tests
# =============================================================================


def test_available_samples_returns_reader_available_count():
    """
    Validates: available_samples() returns the multi_reader.available_count value.

    Synthetic Input:
        - multi_reader.available_count = 1024

    Prediction:
        Returns 1024.
    """
    # Arrange
    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.multi_reader = Mock()
        sx.multi_reader.available_count = 1024

        # Act
        result = sx.available_samples()

        # Assert
        assert result == 1024


def test_available_samples_returns_zero_when_no_samples():
    """
    Validates: available_samples() returns 0 when buffer is empty.

    Synthetic Input:
        - multi_reader.available_count = 0

    Prediction:
        Returns 0.
    """
    # Arrange
    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.multi_reader = Mock()
        sx.multi_reader.available_count = 0

        # Act
        result = sx.available_samples()

        # Assert
        assert result == 0


def test_available_samples_returns_large_buffer_count():
    """
    Validates: available_samples() handles large buffer counts.

    Synthetic Input:
        - multi_reader.available_count = 1000000 (1 million samples)

    Prediction:
        Returns 1000000.
    """
    # Arrange
    with patch('opendaq.Instance'):
        sx = SiriusX()
        sx.multi_reader = Mock()
        sx.multi_reader.available_count = 1000000

        # Act
        result = sx.available_samples()

        # Assert
        assert result == 1000000
