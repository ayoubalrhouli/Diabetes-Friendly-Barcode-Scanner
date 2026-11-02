# Diabetes-Friendly Barcode Scanner (CarboScan)

CarboScan Vision is a computer vision application designed to assist individuals with Type 1 Diabetes in monitoring their carbohydrate intake.

The system uses real-time barcode detection through a webcam and retrieves nutritional information from the [OpenFoodFacts](https://world.openfoodfacts.org/) database. Based on the carbohydrate content, the application classifies food products and provides recommended portion sizes.

The application is a Python desktop app that combines computer vision techniques with a graphical user interface built in Tkinter.

> **Disclaimer:** This is an educational project and not a medical device. It does not replace advice from a doctor or diabetes care team.

## Features

- Real-time barcode detection using a webcam
- Image preprocessing (grayscale conversion, Gaussian blur, adaptive thresholding)
- Automatic carbohydrate classification (Low / Medium / High)
- Recommended portion size calculation
- Daily carbohydrate tracking
- Scan history with timestamps
- Graphical user interface (Tkinter)
- Persistent data storage using JSON

## Tech Stack

Python · OpenCV · Pyzbar · Pillow · Requests · Tkinter · OpenFoodFacts API

## Requirements

- Operating system: Windows / macOS / Linux
- Python 3.9 or higher
- Webcam (integrated or external, 720p recommended)
- Internet connection (required for the OpenFoodFacts API)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ayoubalrhouli/Diabetes-Friendly-Barcode-Scanner.git
   cd Diabetes-Friendly-Barcode-Scanner/Code
   ```

2. **Install the Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the ZBar library** (needed by Pyzbar)
   - Windows: nothing extra, it is included with `pyzbar`
   - macOS: `brew install zbar`
   - Linux: `sudo apt-get install libzbar0`

## Usage

From the `Code` folder, run:

```bash
python carboscan.py
```

Point a product barcode at the webcam and the app will detect it, fetch its nutritional information and show the carbohydrate class and recommended portion.

## Notes
- An internet connection is required to retrieve product information.
- Some products may not be available in the OpenFoodFacts database.
- Detection performance depends on lighting conditions and camera quality.
