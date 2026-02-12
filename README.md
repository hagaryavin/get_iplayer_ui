# get_iplayer_ui 🎧
A graphical interface for downloading BBC programmes using get_iplayer.

## Features:
- Search programmes by name, channel, or type (radio / TV) 
- Display programme details including: 
    - Title, description, duration 
    - High‑resolution images 
    - Track list (when available) 
- Multi‑selection download support 
- PID lookup mode - fetch details directly by programme ID 
- Automatic detection of previously downloaded programmes
- Ability to change the output folder
- Windows launcher for easy startup 

## Technologies Used:
- **Python 3.8+** 
- **PyQt5** for graphical user interface 
- **requests** for fetching metadata and images 
- **get_iplayer** for backend downloader 
- **ffmpeg** & **AtomicParsley** for media processing 
- **Custom scraping logic** for programme metadata (basic + detailed) 
- **Filesystem integration** for reading download history

## Requirements:
- Python 3.8+
- get_iplayer installed on your system
- ffmpeg and AtomicParsley installed

## Installation:
```bash
pip install -r requirements.txt
```

## Running:
- From the command line:
```bash
python main.py
```
- Or double-click on the included `run_app.bat` file

## Acknowledgements:
This project uses **get_iplayer**, an open‑source BBC programme downloader.

Copyright © 2008‑2010 Phil Lewis, 2010‑present get_iplayer contributors  

