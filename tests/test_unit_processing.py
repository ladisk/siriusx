"""
Unit tests for sensitivity processing in SiriusX.

These tests validate the _apply_sensitivity() method which converts
raw voltage signals to physical units based on sensor sensitivity.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add src to path to avoid conflict with empty siriusx.py in root
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from siriusx import SiriusX


class TestApplySensitivity:
    """Tests for SiriusX._apply_sensitivity() method."""

    @pytest.fixture
    def siriusx_with_channel_settings(self):
        """
        Create a SiriusX instance with channel_settings populated.
        We bypass __init__ device connection for unit testing.
        """
        # Create instance and manually set channel_settings
        # (we'll mock the opendaq parts)
        sx = object.__new__(SiriusX)
        sx.channel_settings = {}
        return sx

    # =========================================================================
    # ACCELERATION TESTS - mV/g sensitivity
    # =========================================================================

    def test_apply_sensitivity_iepe_mvg_to_g(self, siriusx_with_channel_settings):
        """
        Validates: IEPE signal with mV/g sensitivity converts correctly to g.

        Synthetic Input:
            - signal: [100.0, 200.0, -50.0] (mV values)
            - sensitivity: 100 mV/g
            - sensitivity_unit: 'mV/g'
            - output_unit: 'g'

        Prediction:
            [1.0, 2.0, -0.5] (signal / sensitivity)
        """
        # Arrange
        sx = siriusx_with_channel_settings
        sx.channel_settings[0] = {
            'Sensitivity': 100,
            'Sensitivity Unit': 'mV/g',
            'Unit': 'g',
        }
        signal = np.array([100.0, 200.0, -50.0])

        # Act
        result = sx._apply_sensitivity(ch_num=0, signal=signal)

        # Assert
        expected = np.array([1.0, 2.0, -0.5])
        np.testing.assert_array_almost_equal(result, expected)

    def test_apply_sensitivity_iepe_mvg_to_ms2(self, siriusx_with_channel_settings):
        """
        Validates: IEPE signal with mV/g sensitivity converts to m/s^2.

        Synthetic Input:
            - signal: [100.0, 200.0] (mV values)
            - sensitivity: 100 mV/g
            - sensitivity_unit: 'mV/g'
            - output_unit: 'm/s^2'

        Prediction:
            [9.81, 19.62] (signal / sensitivity * 9.81)
            Because: 100mV / 100(mV/g) = 1g, and 1g = 9.81 m/s^2
        """
        # Arrange
        sx = siriusx_with_channel_settings
        sx.channel_settings[0] = {
            'Sensitivity': 100,
            'Sensitivity Unit': 'mV/g',
            'Unit': 'm/s^2',
        }
        signal = np.array([100.0, 200.0])

        # Act
        result = sx._apply_sensitivity(ch_num=0, signal=signal)

        # Assert
        expected = np.array([9.81, 19.62])
        np.testing.assert_array_almost_equal(result, expected)

    def test_apply_sensitivity_iepe_mvms2_to_ms2(self, siriusx_with_channel_settings):
        """
        Validates: IEPE signal with mV/(m/s^2) sensitivity converts to m/s^2.

        Synthetic Input:
            - signal: [100.0, 200.0] (mV values)
            - sensitivity: 10 mV/(m/s^2)
            - sensitivity_unit: 'mV/(m/s^2)'
            - output_unit: 'm/s^2'

        Prediction:
            [10.0, 20.0] (signal / sensitivity, same units)
        """
        # Arrange
        sx = siriusx_with_channel_settings
        sx.channel_settings[0] = {
            'Sensitivity': 10,
            'Sensitivity Unit': 'mV/(m/s^2)',
            'Unit': 'm/s^2',
        }
        signal = np.array([100.0, 200.0])

        # Act
        result = sx._apply_sensitivity(ch_num=0, signal=signal)

        # Assert
        expected = np.array([10.0, 20.0])
        np.testing.assert_array_almost_equal(result, expected)

    @pytest.mark.xfail(reason="BUG: sens_unit parsing fails for 'mV/(m/s^2)' - splits incorrectly")
    def test_apply_sensitivity_iepe_mvms2_to_g(self, siriusx_with_channel_settings):
        """
        Validates: IEPE signal with mV/(m/s^2) sensitivity converts to g.

        Synthetic Input:
            - signal: [98.1, 196.2] (mV values)
            - sensitivity: 10 mV/(m/s^2)
            - sensitivity_unit: 'mV/(m/s^2)'
            - output_unit: 'g'

        Prediction:
            [1.0, 2.0] ((signal / sensitivity) / 9.81)
            Because: 98.1mV / 10(mV/(m/s^2)) = 9.81 m/s^2 = 1g

        KNOWN BUG:
            core.py line ~487: sens_unit.split('/')[-1] fails for 'mV/(m/s^2)'
            'mV/(m/s^2)'.split('/') = ['mV', '(m', 's^2)'] -> wrong parsing
            Currently returns [9.81, 19.62] instead of [1.0, 2.0]
        """
        # Arrange
        sx = siriusx_with_channel_settings
        sx.channel_settings[0] = {
            'Sensitivity': 10,
            'Sensitivity Unit': 'mV/(m/s^2)',
            'Unit': 'g',
        }
        signal = np.array([98.1, 196.2])

        # Act
        result = sx._apply_sensitivity(ch_num=0, signal=signal)

        # Assert - Expected correct behavior (currently fails due to bug)
        expected = np.array([1.0, 2.0])
        np.testing.assert_array_almost_equal(result, expected)

    # =========================================================================
    # VOLTAGE TESTS
    # =========================================================================

    def test_apply_sensitivity_voltage_vv(self, siriusx_with_channel_settings):
        """
        Validates: Voltage signal with V/V sensitivity (passthrough).

        Synthetic Input:
            - signal: [1.0, 2.5, -0.5] (V values)
            - sensitivity: 1 V/V
            - sensitivity_unit: 'V/V'
            - output_unit: 'V'

        Prediction:
            [1.0, 2.5, -0.5] (signal / sensitivity = signal when sens=1)
        """
        # Arrange
        sx = siriusx_with_channel_settings
        sx.channel_settings[0] = {
            'Sensitivity': 1,
            'Sensitivity Unit': 'V/V',
            'Unit': 'V',
        }
        signal = np.array([1.0, 2.5, -0.5])

        # Act
        result = sx._apply_sensitivity(ch_num=0, signal=signal)

        # Assert
        expected = np.array([1.0, 2.5, -0.5])
        np.testing.assert_array_almost_equal(result, expected)

    def test_apply_sensitivity_voltage_with_gain(self, siriusx_with_channel_settings):
        """
        Validates: Voltage signal with sensitivity != 1 (scaling factor).

        Synthetic Input:
            - signal: [2.0, 4.0, -1.0] (V values)
            - sensitivity: 2 V/V
            - sensitivity_unit: 'V/V'
            - output_unit: 'V'

        Prediction:
            [1.0, 2.0, -0.5] (signal / sensitivity)
        """
        # Arrange
        sx = siriusx_with_channel_settings
        sx.channel_settings[0] = {
            'Sensitivity': 2,
            'Sensitivity Unit': 'V/V',
            'Unit': 'V',
        }
        signal = np.array([2.0, 4.0, -1.0])

        # Act
        result = sx._apply_sensitivity(ch_num=0, signal=signal)

        # Assert
        expected = np.array([1.0, 2.0, -0.5])
        np.testing.assert_array_almost_equal(result, expected)

    # =========================================================================
    # ARBITRARY UNITS TESTS
    # =========================================================================

    def test_apply_sensitivity_arbitrary_units(self, siriusx_with_channel_settings):
        """
        Validates: Arbitrary unit passthrough (just divides by sensitivity).

        Synthetic Input:
            - signal: [100.0, 200.0] (arbitrary values)
            - sensitivity: 50
            - sensitivity_unit: 'mV/Pa'
            - output_unit: 'Pa'

        Prediction:
            [2.0, 4.0] (signal / sensitivity)
        """
        # Arrange
        sx = siriusx_with_channel_settings
        sx.channel_settings[0] = {
            'Sensitivity': 50,
            'Sensitivity Unit': 'mV/Pa',
            'Unit': 'Pa',
        }
        signal = np.array([100.0, 200.0])

        # Act
        result = sx._apply_sensitivity(ch_num=0, signal=signal)

        # Assert
        expected = np.array([2.0, 4.0])
        np.testing.assert_array_almost_equal(result, expected)
