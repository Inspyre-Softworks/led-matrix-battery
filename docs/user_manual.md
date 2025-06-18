# LED Matrix Battery Monitor - User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Hardware Setup](#hardware-setup)
3. [Software Installation](#software-installation)
4. [System Configuration](#system-configuration)
5. [Using the Features](#using-the-features)
6. [Troubleshooting](#troubleshooting)

## Introduction

The LED Matrix Battery Monitor is now split into two Python packages.  The
`matrix_display` package handles controlling LED matrix hardware and animations
while `power_monitor` provides the battery monitoring logic.  Together they
function just like the original single package.

## Hardware Setup

### Required Components
- LED Matrix display compatible with this software
- USB cable for connecting the LED Matrix to your computer
- Computer with available USB port

### Connection Steps
1. Identify the correct USB port on your computer. The application supports multiple LED matrices connected simultaneously.
2. Connect the LED Matrix to your computer using the USB cable.
3. Verify that the LED Matrix is recognized by your operating system:
   - On Windows: Check Device Manager under "Ports (COM & LPT)"
   - On macOS: Open Terminal and run `ls /dev/tty.*`
   - On Linux: Open Terminal and run `ls /dev/ttyUSB*` or `ls /dev/ttyACM*`
4. Note the port name (e.g., COM3, /dev/ttyUSB0) as you may need it for configuration.

### Physical Placement
- Position the LED Matrix where it's easily visible
- Ensure the USB cable doesn't create strain on the connections
- Keep the LED Matrix away from liquids and extreme temperatures

## Software Installation

### System Requirements
- Windows 10/11, macOS 10.14+, or Linux
- Python 3.7 or higher
- 50MB of free disk space

### Installation Steps

#### Using pip
```bash
pip install led-matrix-battery
```

#### From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/Inspyre-Softworks/led-matrix-battery.git
   cd led-matrix-battery
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

### Verifying Installation
To verify that the installation was successful, run:
```bash
python -m matrix_display.tools.identify
```

This command should detect your connected LED Matrix and display identification information on it.

## System Configuration

### Configuration File
The application uses a configuration file located at:
- Windows: `%APPDATA%\LEDMatrixLib\config.json`
- macOS: `~/Library/Application Support/LEDMatrixLib/config.json`
- Linux: `~/.config/LEDMatrixLib/config.json`

### Basic Configuration Options
- `brightness`: Set the brightness level (0-100)
- `check_interval`: How often to check battery status (in seconds)
- `animations`: Enable/disable animations
- `sound_notifications`: Enable/disable sound notifications

### Example Configuration
```json
{
  "brightness": 75,
  "check_interval": 60,
  "animations": true,
  "sound_notifications": true,
  "devices": {
    "COM3": {
      "enabled": true,
      "side": "left",
      "slot": 1
    }
  }
}
```

### Applying Configuration Changes
Configuration changes are applied automatically when the application is restarted. To restart the application:
1. Close any running instances
2. Launch the application again using the methods described in the next section

## Using the Features

### Starting the Battery Monitor
To start the battery monitor:
```bash
python -m power_monitor
```

Or use the provided script:
```bash
Scripts/battery_monitor.py
```

### Understanding the Display
- **Battery Level**: The number of lit LEDs indicates the current battery percentage
- **Charging Status**: Different animations indicate whether the device is charging or discharging
- **Critical Battery**: Special animation when battery level is critically low

### Available Commands
- `--help`: Display help information
- `--brightness VALUE`: Set the brightness level (0-100)
- `--identify`: Make the LED Matrix display its identification information
- `--clear`: Clear the LED Matrix display

### Customizing Animations
You can customize animations by creating or modifying preset files in the `presets` directory. Each preset is a JSON file that defines animation frames and timing.

To install sample presets:
```bash
install-presets
```

## Troubleshooting

### Common Issues

#### LED Matrix Not Detected
1. Check the USB connection
2. Verify that the device appears in your system's device list
3. Try a different USB port
4. Restart the application

#### Incorrect Display
1. Verify the configuration file has the correct device information
2. Check that the brightness setting is appropriate for your environment
3. Try running the identify command to ensure the correct device is being used

#### Application Crashes
1. Check the log file at `%APPDATA%\LEDMatrixLib\logs\` (Windows) or equivalent
2. Verify that you're using a compatible Python version
3. Reinstall the application

### Getting Help
If you encounter issues not covered in this troubleshooting section, please:
1. Check the GitHub repository for known issues
2. Submit a new issue with detailed information about your problem
3. Include log files and system information in your report