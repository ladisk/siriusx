# Sirius X Network Setup Guide

This document describes how to configure network connectivity for the Dewesoft Sirius X data acquisition device when connecting via a USB ethernet adapter.

## Problem Symptoms

When the Sirius X device is not properly configured for network access, you may encounter:

1. **Device discovery works but connection fails**:
   ```
   [NativeStreamingClientImpl] [error] Connect operation failed Connection refused
   ```

2. **USB ethernet adapter stuck in "getting IP configuration"**:
   ```
   $ nmcli device status
   enx00249b891d28    ethernet  connecting (getting IP configuration)  Wired connection 1
   ```

3. **No IPv4 address on the USB ethernet interface**:
   ```
   $ ip addr show enx00249b891d28
   inet6 fe80::... scope link   # Only IPv6 link-local, no IPv4
   ```

4. **Ping to device fails with "Destination Host Unreachable"**

## Root Cause

The USB ethernet adapter is configured for DHCP by default, but there is no DHCP server on the direct connection to the Sirius X device. The device and PC cannot communicate because they're not on the same IP subnet.

## Device Information

| Property | Value |
|----------|-------|
| Device | Dewesoft Sirius X |
| Serial | DB24050686 |
| Connection String | `daq://Dewesoft_DB24050686` |
| **Device IP** | `192.168.10.1` (custom configuration) |
| Default IP (factory) | `192.168.173.1` |

**Note**: This specific device was previously configured with IP `192.168.10.1`, not the factory default `192.168.173.1`. If the device is factory reset, it will revert to `192.168.173.1`.

## Hardware Setup

- **USB Ethernet Adapter**: `enx00249b891d28` (name based on MAC address)
- **Connection**: Direct ethernet cable from USB adapter to Sirius X device
- **Power**: Sirius X requires PoE (Power over Ethernet) or external power supply

## Solution: Configure Static IP

### Step 1: Identify the USB Ethernet Adapter

```bash
# List all network interfaces
ip link show

# Check NetworkManager device status
nmcli device status
```

Look for an interface named `enxXXXXXXXXXXXX` (USB ethernet adapters use this naming convention based on MAC address).

### Step 2: Find the Device's IP Address

First, try to discover what IP the device is using:

```bash
# Use opendaq to discover devices (works across subnets)
uv run python -c "
import opendaq
instance = opendaq.Instance()
for d in instance.available_devices:
    if 'Dewesoft' in d.connection_string:
        print(f'{d.connection_string}: {d.name}')
"

# Check ARP table after discovery attempt
ip neigh show dev enx00249b891d28
```

The ARP table will show the device's actual IP address.

### Step 3: Configure Static IP on USB Adapter

Configure the USB ethernet adapter with a static IP in the same subnet as the device:

```bash
# For device at 192.168.10.1 (current configuration)
nmcli connection modify "Wired connection 1" \
    ipv4.method manual \
    ipv4.addresses 192.168.10.2/24 \
    ipv4.gateway ""

# Apply the changes
nmcli connection up "Wired connection 1"
```

If the device is at the factory default (`192.168.173.1`):

```bash
# For device at 192.168.173.1 (factory default)
nmcli connection modify "Wired connection 1" \
    ipv4.method manual \
    ipv4.addresses 192.168.173.2/24 \
    ipv4.gateway ""

nmcli connection up "Wired connection 1"
```

### Step 4: Add Multiple IP Addresses (Optional)

If you're unsure which IP the device is using, you can add multiple addresses:

```bash
# Add both subnets to cover both possibilities
nmcli connection modify "Wired connection 1" \
    ipv4.method manual \
    ipv4.addresses "192.168.10.2/24,192.168.173.2/24"

nmcli connection up "Wired connection 1"
```

### Step 5: Verify Connectivity

```bash
# Check IP addresses are configured
ip addr show enx00249b891d28

# Verify link is up
ethtool enx00249b891d28 | grep -E "(Link detected|Speed)"

# Ping the device
ping -c 3 192.168.10.1    # or 192.168.173.1 for factory default

# Test with SiriusX
uv run python -c "
from siriusx import SiriusX
sx = SiriusX()
sx.connect('daq://Dewesoft_DB24050686')
print(f'Connected: {sx.connected}')
print(f'Sample rate: {sx.get_sample_rate()} Hz')
sx.cleanup()
"
```

## Quick Setup Commands (Copy-Paste)

For this specific setup (device at `192.168.10.1`):

```bash
# Configure and activate
nmcli connection modify "Wired connection 1" \
    ipv4.method manual \
    ipv4.addresses "192.168.10.2/24,192.168.173.2/24" \
    ipv4.gateway ""
nmcli connection up "Wired connection 1"

# Verify
ping -c 2 192.168.10.1
```

## Reverting to DHCP (if needed)

To restore DHCP configuration:

```bash
nmcli connection modify "Wired connection 1" \
    ipv4.method auto \
    ipv4.addresses ""

nmcli connection up "Wired connection 1"
```

## Troubleshooting

### Device Not Discovered by opendaq

1. Check physical connection (ethernet cable)
2. Verify link is detected: `ethtool enx00249b891d28 | grep "Link detected"`
3. Check firewall isn't blocking discovery

### Device Discovered but Connection Refused

1. Check ARP table for device's actual IP: `ip neigh show dev enx00249b891d28`
2. Ensure PC has an IP in the same subnet as the device
3. Verify with ping before attempting connection

### Connection Works Initially but Drops

1. Ensure NetworkManager configuration is persistent (use `nmcli connection modify`, not `ip addr add`)
2. Check for IP conflicts with other interfaces
3. Verify no other DHCP server is interfering

## Network Configuration Summary

### Current Working Configuration

| Interface | Connection Name | IP Addresses | Purpose |
|-----------|-----------------|--------------|---------|
| `enx00249b891d28` | Wired connection 1 | `192.168.10.2/24`, `192.168.173.2/24` | Sirius X connection |
| `enp44s0` | Wired connection 2 | DHCP | Regular network |
| `wlp0s20f3` | eduroam | DHCP | WiFi |

### Sirius X Network Defaults (Reference)

From Dewesoft documentation:
- **Default IP**: `192.168.173.1`
- **Connectivity**: Gigabit Ethernet with PoE support
- **Discovery**: Automatic via Dewesoft X software or opendaq SDK
- **Configuration**: No web interface; use Dewesoft X software to change device IP

## Offline Documentation

The following manuals are stored locally in `docs/manuals/`:

- `dewesoft-sirius-x-manual-en.pdf` - Sirius X Technical Reference Manual
- `dewesoft-sirius-manual-en.pdf` - Sirius General Manual

## References

- [Dewesoft SIRIUS X Product Page](https://dewesoft.com/products/sirius-x)
- [Network and Firewall Rules for Dewesoft Devices](https://manual.dewesoft.com/x/setupmodule/devices/network-and-firewall-rules-for-use-of-dewesoft-devices)
- [Add Device - Dewesoft X Manual](https://manual.dewesoft.com/x/setupmodule/devices/adddevice)
- [PoE and PTP v2 in Data Acquisition](https://dewesoft.com/blog/poe-and-ptp-in-data-acquisition)
