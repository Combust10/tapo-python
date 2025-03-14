# Tapo Smart Bulb Control Script

This repository contains a Python script to control a Tapo smart bulb (L530) using the Tapo API. The script allows you to toggle the bulb's state, retrieve device information, and run an ambient lighting mode that changes the bulb's color based on the dominant color of your screen.

## Features

- **Toggle Bulb State**: Turn the bulb on or off.
- **Device Info**: Retrieve and display the bulb's current state and information.
- **Ambient Lighting**: Automatically adjust the bulb's color to match the dominant color of your screen in real-time.

## Requirements

- Python 3.7+
- Required Python packages:
  - `tapo`
  - `Pillow`
  - `numpy`
  - `numexpr`
  - `mss`
  - `dxcam`
  - `pyautogui`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Combust10/tapo-python-ambient.git
cd tapo-python-ambient
```

### Install the required packages:
```bash
pip install -r requirements.txt
```
### Set up environment variables:
Create a .env file in the root directory with the following content:
```bash
API_EMAIL=your_email@example.com
API_PASSWORD=your_password
DEVICE_IP=192.168.1.xxx
```

## Usage

Run the script:
```bash
python tapo_control.py
```
## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.


## Acknowledgments

- [Tapo API Client](https://github.com/mihai-dinculescu/tapo)
- [Pillow](https://python-pillow.org/)
- [NumPy](https://numpy.org/)
- [dxcam](https://github.com/ra1nty/DXcam)
