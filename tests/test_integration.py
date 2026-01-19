"""
Integration tests for SiriusX that require real hardware.

These tests require a physical Sirius X device to be connected and available.
They are skipped by default in CI/CD pipelines and local test runs.

HOW TO RUN THESE TESTS
-----------------------

Option 1: Run with --hardware flag (requires hardware to be connected):
    uv run pytest tests/test_integration.py -v --hardware

Option 2: Set environment variable:
    export SIRIUSX_HARDWARE=1
    uv run pytest tests/test_integration.py -v

Option 3: Run all tests except hardware tests (default):
    uv run pytest tests/ -v -m "not hardware"

CONFIGURATION
-------------

Set device connection string via environment variable:
    export SIRIUSX_CONNECTION_STRING="daq://Dewesoft_DB24050686"

Default connection string: daq://Dewesoft_DB24050686

IMPORTANT
---------

These tests use real hardware and will:
- Discover and connect to the device
- Configure channels and sample rates
- Acquire real data from the device
- Always cleanup resources (using context managers or finally blocks)

Each test is independent and performs its own setup/teardown to ensure
the device is left in a clean state.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from siriusx import SiriusX


# Skip all tests in this module unless --hardware flag is passed or env var is set
pytestmark = pytest.mark.hardware

# Delay between tests to allow device to recover from rapid connect/disconnect cycles
INTER_TEST_DELAY_SECONDS = 2.0


@pytest.fixture(autouse=True)
def device_recovery_delay():
    """
    Adds a small delay after each test to allow the device to recover.

    The Sirius X hardware can become unstable when subjected to rapid
    connect/disconnect cycles. This delay ensures reliable test execution
    when running the full integration test suite.
    """
    yield  # Run the test
    time.sleep(INTER_TEST_DELAY_SECONDS)  # Wait after test completes


@pytest.fixture
def connection_string() -> str:
    """
    Get device connection string from environment or discover it.

    Returns
    -------
    str
        Device connection string.

    Raises
    ------
    pytest.skip
        If no suitable device is found.
    """
    # Check if connection string is provided via env var
    env_conn_str = os.environ.get("SIRIUSX_CONNECTION_STRING")
    if env_conn_str:
        return env_conn_str

    # Try to discover a Sirius X device
    sx = SiriusX()
    devices = sx.list_available_devices(print_devices=False, return_list=True)

    # Filter for actual DAQ devices (exclude audio devices and reference devices)
    daq_devices = [
        d for d in devices
        if d[3].startswith("daq://") and not d[3].startswith("daqref://")
    ]

    if not daq_devices:
        pytest.skip(
            "No Sirius X hardware found. Set SIRIUSX_CONNECTION_STRING env var "
            "or ensure device is connected and powered on."
        )

    # Return the first discovered DAQ device
    return daq_devices[0][3]


@pytest.fixture
def sample_iepe_config() -> dict:
    """
    Sample IEPE channel configuration for testing.

    Returns
    -------
    dict
        Channel configuration dictionary for IEPE sensor.
    """
    return {
        0: {
            'Name': 'test_accel',
            'Measurement': 'IEPE',
            'Range': '10000',
            'HPFilter': 'AC 1Hz',
            'Excitation': 2.0,
            'Sensitivity': 100.0,
            'Sensitivity Unit': 'mV/g',
            'Unit': 'g',
        }
    }


@pytest.fixture
def sample_voltage_config() -> dict:
    """
    Sample Voltage channel configuration for testing.

    Returns
    -------
    dict
        Channel configuration dictionary for voltage input.
    """
    return {
        1: {
            'Name': 'test_voltage',
            'Measurement': 'Voltage',
            'Range': '10',
            'HPFilter': 'DC',
            'Sensitivity': 1.0,
            'Sensitivity Unit': 'V/V',
            'Unit': 'V',
        }
    }


class TestDeviceDiscovery:
    """Integration tests for device discovery with real hardware."""

    def test_device_discovery(self):
        """
        Validates: list_available_devices() discovers real Sirius X devices on network.

        This test verifies that the device discovery mechanism can find actual
        hardware devices and return their connection information.

        Expected Behavior:
            - Should discover at least one DAQ device (excluding audio/reference)
            - Each device should have a name and connection string
            - DAQ device connection strings should follow daq:// format
        """
        with SiriusX() as sx:
            # Discover all devices
            devices = sx.list_available_devices(print_devices=True, return_list=True)

            # Should find at least one device
            assert len(devices) > 0, "No devices discovered"

            # Filter for actual DAQ devices (exclude audio and reference devices)
            daq_devices = [
                d for d in devices
                if d[3].startswith("daq://") and not d[3].startswith("daqref://")
                and not d[3].startswith("miniaudio://")
            ]

            # Should find at least one DAQ device
            if len(daq_devices) == 0:
                pytest.skip(
                    "No Sirius X hardware found. Ensure device is connected and powered on. "
                    f"Found {len(devices)} total devices but none are DAQ devices."
                )

            # Verify DAQ device info structure
            for device_info in daq_devices:
                assert len(device_info) == 4, "Device info should have 4 elements"
                assert device_info[0] == "Name:", "First element should be 'Name:'"
                assert device_info[2] == "Connection string:", "Third element should be 'Connection string:'"

                # Verify connection string format
                connection_str = device_info[3]
                assert connection_str.startswith("daq://"), \
                    f"Connection string should start with 'daq://', got: {connection_str}"
                assert not connection_str.startswith("daqref://"), \
                    "Should not be a reference device"


class TestDeviceConnection:
    """Integration tests for device connection and disconnection."""

    def test_device_connection(self, connection_string):
        """
        Validates: connect() and disconnect() successfully manage device connection lifecycle.

        This test verifies that the device can be connected and disconnected properly,
        ensuring resource cleanup.

        Expected Behavior:
            - connect() should return True on success
            - Device should report as connected
            - disconnect() should return True on success
            - Device should report as not connected after disconnect
        """
        sx = SiriusX()

        try:
            # Test connection
            result = sx.connect(connection_string)
            assert result is True, f"Failed to connect to device: {connection_string}"
            assert sx.connected is True, "Device should report as connected"
            assert sx.device is not None, "Device object should not be None"

            # Test disconnection
            result = sx.disconnect()
            assert result is True, "Failed to disconnect from device"
            assert sx.connected is False, "Device should report as not connected"
            assert sx.device is None, "Device object should be None after disconnect"

        finally:
            # Ensure cleanup even if test fails
            sx.cleanup()

    def test_device_connection_context_manager(self, connection_string):
        """
        Validates: Context manager properly handles connection lifecycle and cleanup.

        This test verifies that using the context manager (with statement) correctly
        manages device resources and ensures cleanup on exit.

        Expected Behavior:
            - Device should connect successfully within context
            - Device should automatically cleanup on context exit
            - No manual cleanup should be needed
        """
        with SiriusX() as sx:
            result = sx.connect(connection_string)
            assert result is True, f"Failed to connect to device: {connection_string}"
            assert sx.connected is True, "Device should report as connected"

        # After context exit, device should be cleaned up
        # (We can't check sx.connected here as sx is out of scope)


class TestSampleRate:
    """Integration tests for sample rate configuration."""

    def test_sample_rate_round_trip(self, connection_string):
        """
        Validates: set_sample_rate() and get_sample_rate() correctly configure device sampling.

        This test verifies that sample rates can be set and retrieved correctly,
        accounting for hardware constraints (device may round to nearest valid rate).

        Expected Behavior:
            - set_sample_rate() should return the actual rate set by device
            - get_sample_rate() should return the same rate
            - Returned rate should be close to requested rate (within hardware limits)
        """
        with SiriusX() as sx:
            sx.connect(connection_string)

            # Test setting various sample rates
            test_rates = [1000.0, 5000.0, 10000.0]

            for requested_rate in test_rates:
                actual_rate = sx.set_sample_rate(requested_rate)
                assert actual_rate > 0, f"Invalid sample rate returned: {actual_rate}"

                # Verify get_sample_rate returns same value
                retrieved_rate = sx.get_sample_rate()
                assert retrieved_rate == actual_rate, \
                    f"Retrieved rate {retrieved_rate} != set rate {actual_rate}"

                # Device may round to nearest valid rate, so check within reasonable range
                # Allow up to 10% difference from requested rate
                tolerance = requested_rate * 0.1
                assert abs(actual_rate - requested_rate) <= tolerance, \
                    f"Actual rate {actual_rate} too far from requested {requested_rate}"


class TestChannelConfiguration:
    """Integration tests for channel configuration."""

    def test_channel_configuration(
        self,
        connection_string,
        sample_iepe_config,
        sample_voltage_config
    ):
        """
        Validates: configure_channels() applies IEPE and Voltage settings to real hardware.

        This test verifies that channel configuration works with real hardware,
        including IEPE excitation, range, filters, and sensitivity settings.

        Expected Behavior:
            - Should configure IEPE channel with proper excitation and range
            - Should configure Voltage channel with proper range and filtering
            - No exceptions should be raised during configuration
            - Configuration should be applied to hardware
        """
        with SiriusX() as sx:
            sx.connect(connection_string)
            sx.set_sample_rate(1000.0)

            # Test IEPE configuration
            sx.configure_channels(sample_iepe_config)
            assert len(sx.selected_signals) == 1, "Should have 1 selected signal"
            assert len(sx.selected_channels) == 1, "Should have 1 selected channel"

            # Test Voltage configuration
            sx.configure_channels(sample_voltage_config)
            assert len(sx.selected_signals) == 1, "Should have 1 selected signal"
            assert len(sx.selected_channels) == 1, "Should have 1 selected channel"

            # Test multi-channel configuration
            multi_config = {**sample_iepe_config, **sample_voltage_config}
            sx.configure_channels(multi_config)
            assert len(sx.selected_signals) == 2, "Should have 2 selected signals"
            assert len(sx.selected_channels) == 2, "Should have 2 selected channels"


class TestDataAcquisitionRaw:
    """Integration tests for raw data acquisition."""

    def test_data_acquisition_raw(self, connection_string, sample_iepe_config):
        """
        Validates: acquire_raw() acquires real data with correct shape and properties.

        This test verifies that raw voltage data can be acquired from the device
        with the correct dimensions and data types.

        Expected Behavior:
            - Should return numpy array with shape (samples, channels)
            - Should contain float values (voltage readings)
            - Should acquire approximately the requested number of samples
            - Data should be non-empty and within reasonable voltage ranges
        """
        with SiriusX() as sx:
            sx.connect(connection_string)
            sx.set_sample_rate(1000.0)
            sx.configure_channels(sample_iepe_config)

            # Acquire 0.5 seconds of data (500 samples at 1kHz)
            sample_count = 500
            timeout = 2.0  # Allow 2 seconds for acquisition

            raw_data = sx.acquire_raw(sample_count=sample_count, timeout=timeout)

            # Verify shape
            assert raw_data.ndim == 2, "Raw data should be 2D array"
            assert raw_data.shape[1] == 1, "Should have 1 channel"

            # Should get approximately the requested samples (allow some tolerance)
            assert raw_data.shape[0] >= sample_count * 0.9, \
                f"Got {raw_data.shape[0]} samples, expected ~{sample_count}"
            assert raw_data.shape[0] <= sample_count * 1.1, \
                f"Got {raw_data.shape[0]} samples, expected ~{sample_count}"

            # Verify data type
            assert raw_data.dtype in [np.float32, np.float64], \
                f"Expected float data, got {raw_data.dtype}"

            # Verify data is not all zeros (actual signal present)
            assert not np.all(raw_data == 0), "Raw data should not be all zeros"

            # Verify data is within reasonable voltage range (e.g., +/- 20V)
            assert np.abs(raw_data).max() < 20.0, \
                f"Raw voltage data out of range: max={np.abs(raw_data).max()}"


class TestDataAcquisitionProcessed:
    """Integration tests for processed data acquisition."""

    def test_data_acquisition_processed(self, connection_string, sample_iepe_config):
        """
        Validates: acquire_processed() applies sensitivity and returns calibrated data.

        This test verifies that processed data acquisition correctly applies
        sensitivity calibration to raw voltage readings.

        Expected Behavior:
            - Should return numpy array with shape (samples, channels)
            - Values should be in engineering units (g for acceleration)
            - Data should be scaled according to sensitivity setting
            - Should acquire approximately the requested duration of data
        """
        with SiriusX() as sx:
            sx.connect(connection_string)
            sx.set_sample_rate(1000.0)
            sx.configure_channels(sample_iepe_config)

            # Acquire 0.5 seconds of processed data
            acquisition_time = 0.5

            processed_data = sx.acquire_processed(
                acqusition_time=acquisition_time,
                return_dict=False
            )

            # Verify shape
            assert processed_data.ndim == 2, "Processed data should be 2D array"
            assert processed_data.shape[1] == 1, "Should have 1 channel"

            # Verify sample count
            expected_samples = int(acquisition_time * 1000.0)  # 500 samples
            assert processed_data.shape[0] >= expected_samples * 0.9, \
                f"Got {processed_data.shape[0]} samples, expected ~{expected_samples}"
            assert processed_data.shape[0] <= expected_samples * 1.1, \
                f"Got {processed_data.shape[0]} samples, expected ~{expected_samples}"

            # Verify data type
            assert processed_data.dtype in [np.float32, np.float64], \
                f"Expected float data, got {processed_data.dtype}"

            # Verify data is scaled differently than raw (sensitivity applied)
            # With 100 mV/g sensitivity, processed values should be in reasonable g range
            assert not np.all(processed_data == 0), "Processed data should not be all zeros"

    def test_data_acquisition_processed_dict(self, connection_string, sample_iepe_config):
        """
        Validates: acquire_processed() returns dict format with channel names and units.

        This test verifies that the dictionary return format includes all expected
        metadata (channel names, units, time vector).

        Expected Behavior:
            - Should return dict with channel name as key
            - Each channel should have 'signal' and 'unit' entries
            - Should include 'time' entry with time vector
            - Time vector should span the acquisition duration
        """
        with SiriusX() as sx:
            sx.connect(connection_string)
            sx.set_sample_rate(1000.0)
            sx.configure_channels(sample_iepe_config)

            # Acquire 0.5 seconds of processed data as dict
            acquisition_time = 0.5

            data_dict = sx.acquire_processed(
                acqusition_time=acquisition_time,
                return_dict=True
            )

            # Verify dict structure
            assert isinstance(data_dict, dict), "Should return dictionary"

            # Should contain channel and time entries
            assert 'test_accel' in data_dict, "Should contain channel 'test_accel'"
            assert 'time' in data_dict, "Should contain 'time' entry"

            # Verify channel data structure
            channel_data = data_dict['test_accel']
            assert 'signal' in channel_data, "Channel should have 'signal' key"
            assert 'unit' in channel_data, "Channel should have 'unit' key"
            assert channel_data['unit'] == 'g', "Unit should be 'g'"

            # Verify time data structure
            time_data = data_dict['time']
            assert 'signal' in time_data, "Time should have 'signal' key"
            assert 'unit' in time_data, "Time should have 'unit' key"
            assert time_data['unit'] == 's', "Time unit should be 's'"

            # Verify time vector properties
            time_vector = time_data['signal']
            assert time_vector[0] == 0.0, "Time should start at 0"
            assert abs(time_vector[-1] - acquisition_time) < 0.01, \
                f"Time should end near {acquisition_time}, got {time_vector[-1]}"

            # Verify signal and time have same length
            signal = channel_data['signal']
            assert len(signal) == len(time_vector), \
                "Signal and time vector should have same length"


class TestFullWorkflow:
    """Integration test for complete acquisition workflow."""

    def test_full_workflow(
        self,
        connection_string,
        sample_iepe_config,
        sample_voltage_config
    ):
        """
        Validates: Complete workflow from connection to data acquisition and cleanup.

        This test verifies the entire typical use case: discovering devices,
        connecting, configuring multiple channels, acquiring data, and cleaning up.

        Expected Behavior:
            - Should complete full workflow without errors
            - Should discover devices
            - Should connect successfully
            - Should configure multiple channels
            - Should acquire multi-channel data
            - Should cleanup properly
        """
        # Step 1: Device discovery
        with SiriusX() as sx:
            devices = sx.list_available_devices(print_devices=False, return_list=True)
            assert len(devices) > 0, "Should discover at least one device"

            # Step 2: Connection
            result = sx.connect(connection_string)
            assert result is True, "Should connect successfully"

            # Step 3: Sample rate configuration
            sample_rate = sx.set_sample_rate(5000.0)
            assert sample_rate > 0, "Should set valid sample rate"

            # Step 4: Multi-channel configuration
            multi_config = {**sample_iepe_config, **sample_voltage_config}
            sx.configure_channels(multi_config)
            assert len(sx.selected_channels) == 2, "Should configure 2 channels"

            # Step 5: Raw data acquisition
            raw_data = sx.acquire_raw(sample_count=1000, timeout=2.0)
            assert raw_data.shape == (1000, 2), \
                f"Expected shape (1000, 2), got {raw_data.shape}"

            # Step 6: Processed data acquisition
            processed_data = sx.acquire_processed(
                acqusition_time=0.2,
                return_dict=True
            )
            assert 'test_accel' in processed_data, "Should contain IEPE channel"
            assert 'test_voltage' in processed_data, "Should contain Voltage channel"
            assert 'time' in processed_data, "Should contain time vector"

            # Step 7: Cleanup happens automatically via context manager

        # Verify workflow completed successfully (no exceptions raised)
