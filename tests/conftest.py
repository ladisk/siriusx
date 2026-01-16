"""
Shared fixtures and mock factories for siriusx tests.

=============================================================================
TEST VALIDATION WORKFLOW - ALL TESTS MUST FOLLOW THIS
=============================================================================

Every test function MUST have:

1. A docstring with:
   - "Validates:" section describing what behavior is tested
   - "Synthetic Input:" section with concrete mock values
   - "Prediction:" section with expected outcome

2. The test must be run INDIVIDUALLY first:
   uv run pytest tests/file.py::test_name -v

3. Verify actual result matches prediction before committing

Example:
    def test_something():
        \"\"\"
        Validates: Function X returns Y when given Z.

        Synthetic Input:
            - mock_obj.method() returns [1, 2, 3]
            - parameter value is 10

        Prediction:
            Returns [10, 20, 30] (input multiplied by parameter)
        \"\"\"
        # Arrange
        mock_obj.method.return_value = [1, 2, 3]

        # Act
        result = function_x(mock_obj, 10)

        # Assert
        assert result == [10, 20, 30]

=============================================================================
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np


# =============================================================================
# MOCK FACTORIES
# =============================================================================

@pytest.fixture
def mock_property():
    """
    Factory for creating mock opendaq Property objects.

    Usage:
        prop = mock_property(name="Range", value=0, selection_values=['10', '5', '1'])
    """
    def _create(name: str, value=None, selection_values=None):
        prop = Mock()
        prop.name = name
        prop.value = value
        prop.selection_values = selection_values
        prop.unit = None
        return prop
    return _create


@pytest.fixture
def mock_function_block(mock_property):
    """
    Factory for creating mock Amplifier function blocks.

    Usage:
        fb = mock_function_block(properties={'Measurement': (['Voltage', 'IEPE'], 1)})
    """
    def _create(name: str = "Amplifier", properties: dict = None):
        """
        Args:
            name: Function block name
            properties: Dict of {prop_name: (selection_values, current_value)}
        """
        fb = Mock()
        fb.name = name

        props = []
        if properties:
            for prop_name, (selections, value) in properties.items():
                prop = mock_property(name=prop_name, value=value, selection_values=selections)
                props.append(prop)

        fb.visible_properties = props
        return fb
    return _create


@pytest.fixture
def mock_channel(mock_function_block):
    """
    Factory for creating mock Channel objects.

    Usage:
        chan = mock_channel(name="AI 1", function_blocks=[fb])
    """
    def _create(name: str, global_id: str = None, function_blocks: list = None):
        chan = Mock()
        chan.name = name
        chan.global_id = global_id or f"/device/IO/{name}"
        chan.get_function_blocks.return_value = function_blocks or []
        return chan
    return _create


@pytest.fixture
def mock_signal():
    """
    Factory for creating mock Signal objects.

    Usage:
        sig = mock_signal(name="AI 1", global_id="/device/sig/AI1")
    """
    def _create(name: str, global_id: str = None):
        sig = Mock()
        sig.name = name
        sig.global_id = global_id or f"/device/sig/{name}"
        return sig
    return _create


@pytest.fixture
def mock_device(mock_channel, mock_signal):
    """
    Factory for creating mock Device objects.

    Usage:
        device = mock_device(
            name="SiriusX",
            properties={'SampleRate': 1000},
            channels=[chan1, chan2],
            signals=[sig1, sig2]
        )
    """
    def _create(
        name: str = "MockDevice",
        properties: dict = None,
        channels: list = None,
        signals: list = None
    ):
        device = Mock()
        device.name = name
        device.info = Mock()

        # Properties
        props = properties or {}
        device.get_property_value.side_effect = lambda k: props.get(k)
        device.set_property_value.side_effect = lambda k, v: props.update({k: v})

        # Channels and signals
        device.channels_recursive = channels or []
        device.signals_recursive = signals or []

        return device
    return _create


@pytest.fixture
def mock_device_info():
    """
    Factory for creating mock DeviceInfo objects (for device discovery).

    Usage:
        info = mock_device_info(name="SiriusX-1", connection_string="daq://...")
    """
    def _create(name: str, connection_string: str):
        info = Mock()
        info.name = name
        info.connection_string = connection_string
        return info
    return _create


@pytest.fixture
def mock_instance(mock_device_info):
    """
    Factory for creating mock opendaq.Instance objects.

    Usage:
        instance = mock_instance(available=[info1, info2])
    """
    def _create(available_devices: list = None):
        instance = Mock()
        instance.available_devices = available_devices or []
        instance.add_device = Mock(return_value=Mock())
        return instance
    return _create


@pytest.fixture
def mock_multi_reader():
    """
    Factory for creating mock opendaq.MultiReader objects.

    Usage:
        reader = mock_multi_reader(read_data=np.array([[1,2], [3,4]]))
    """
    def _create(read_data: np.ndarray = None, available_count: int = 0):
        reader = Mock()
        reader.read.return_value = read_data if read_data is not None else np.array([])
        reader.available_count = available_count
        return reader
    return _create


# =============================================================================
# VALIDATION HELPER
# =============================================================================

def validate_test_has_docstring(test_func):
    """
    Helper to check if a test has the required docstring format.
    Can be used in CI or pre-commit hooks.
    """
    doc = test_func.__doc__
    if not doc:
        return False, "Missing docstring"

    required_sections = ["Validates:", "Synthetic Input:", "Prediction:"]
    missing = [s for s in required_sections if s not in doc]

    if missing:
        return False, f"Missing sections: {missing}"

    return True, "OK"
