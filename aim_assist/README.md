# Vision-Based Aim Assist

A Python-based aim assist that uses screen capture and color detection to identify targets and assist with aiming. Designed for private/sandbox games among friends.

## Features

- **Color-based target detection** using HSV color space
- **Smooth mouse movement** with configurable sensitivity and acceleration
- **Head offset** for automatic headshot aiming
- **FOV limiting** to only target enemies within your field of view
- **Target prediction** for moving targets
- **Calibration tool** to easily configure target colors for any game
- **Debug mode** with visual overlay showing detections

## Requirements

- Python 3.10+
- Linux (X11) or Windows

## Installation

```bash
cd aim_assist
pip install -r requirements.txt
```

## Quick Start

### 1. Calibrate Colors (First Time Setup)

Run the calibration tool to configure the target colors for your game:

```bash
python calibrate.py
```

1. Position your game so enemies/targets are visible
2. Click on the target color you want to detect
3. Adjust the tolerance slider until targets are detected well
4. Press `S` to save configuration
5. Press `Q` to quit

### 2. Run the Aim Assist

```bash
# Basic usage (uses saved config)
python aim_assist.py

# With debug visualization
python aim_assist.py --debug

# With specific color preset
python aim_assist.py --color red

# With custom sensitivity
python aim_assist.py --sensitivity 1.2
```

## Controls

| Key | Action |
|-----|--------|
| `Shift` (hold) | Activate aim assist |
| `CapsLock` | Toggle aim assist on/off |
| `End` | Exit program |

## Configuration

Edit `aim_config.json` or use command line arguments:

```json
{
  "capture_width": 320,
  "capture_height": 320,
  "target_color": "red",
  "sensitivity": 0.8,
  "smoothing": 0.3,
  "max_speed": 80,
  "deadzone": 3,
  "aim_at_head": true,
  "head_offset_ratio": 0.35,
  "fov_limit": 150,
  "activation_key": "shift",
  "debug_mode": false
}
```

### Key Settings

| Setting | Description | Range |
|---------|-------------|-------|
| `sensitivity` | How fast the aim moves | 0.1 - 5.0 |
| `smoothing` | Movement smoothness (higher = smoother) | 0.0 - 1.0 |
| `max_speed` | Maximum pixels per frame | 10 - 200 |
| `deadzone` | Ignore targets this close to crosshair | 1 - 20 |
| `fov_limit` | Maximum distance to lock onto targets | 50 - 500 |
| `head_offset_ratio` | How far up to aim for headshots | 0.0 - 0.5 |

### Color Presets

Available presets: `red`, `yellow`, `green`, `orange`, `purple`, `cyan`, `white`

For custom colors, use the calibration tool or set manually:

```json
{
  "target_color": "custom",
  "custom_hsv_lower": [0, 100, 100],
  "custom_hsv_upper": [10, 255, 255]
}
```

## How It Works

1. **Screen Capture**: Captures a region around your crosshair using MSS
2. **Color Detection**: Converts to HSV and finds pixels matching target colors
3. **Target Identification**: Groups detected pixels into contours, filters by size
4. **Target Selection**: Chooses the closest target to crosshair center
5. **Mouse Movement**: Calculates offset and smoothly moves mouse toward target

## Tuning Tips

### For Your Friend's Game

1. **Run in debug mode** first (`--debug`) to see what's being detected
2. **Use the calibrator** to find the exact color of enemy highlights
3. **Start with low sensitivity** (0.5) and increase gradually
4. **Increase smoothing** (0.5+) if movement feels jerky
5. **Adjust FOV limit** based on how far targets appear from center
6. **Tune min/max area** if detecting wrong objects

### If Detection Is Poor

- Increase tolerance in calibrator
- Add multiple color ranges if targets have varying colors
- Ensure the game's enemy highlight color is distinctive

### If Aim Feels Off

- Lower sensitivity for more precision
- Increase smoothing for smoother tracking
- Adjust head_offset_ratio for your game's hitboxes

## File Structure

```
aim_assist/
├── aim_assist.py      # Main controller
├── screen_capture.py  # Screen grabbing module
├── target_detector.py # Color-based detection
├── mouse_controller.py # Mouse movement
├── config.py          # Configuration handling
├── calibrate.py       # Color calibration tool
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Troubleshooting

**"No targets detected"**
- Run calibrator and select the correct color
- Increase tolerance
- Check that enemies have visible highlight colors

**"Aim is too slow/fast"**
- Adjust sensitivity value
- Check your game's mouse sensitivity settings

**"Aim feels jittery"**
- Increase smoothing value
- Increase deadzone value

**"Wrong things being detected"**
- Narrow the color range (lower tolerance)
- Increase min_target_area to filter small objects
- Decrease max_target_area to filter large objects

## License

For personal/private use only. Not intended for use in online competitive games or any game where it would violate terms of service.
