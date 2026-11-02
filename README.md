# Diabetes-Friendly Barcode Scanner (CarboScan)

Project Description:

CarboScan Vision is a computer vision application designed to assist individuals with Type 1 Diabetes in monitoring their carbohydrate intake.

The system uses real-time barcode detection through a webcam and retrieves nutritional information from the OpenFoodFacts database. Based on the carbohydrate content, the application classifies food products and provides recommended portion sizes.

The application is implemented in Python and integrates computer vision techniques with a graphical user interface.

Main Features:

* Real-time barcode detection using a webcam
* Image preprocessing (grayscale conversion, Gaussian blur, adaptive thresholding)
* Automatic carbohydrate classification (Low / Medium / High)
* Recommended portion size calculation
* Daily carbohydrate tracking
* Scan history with timestamps
* Graphical User Interface (Tkinter)
* Persistent data storage using JSON

System Requirements:

* Operating System: Windows / macOS / Linux
* Python Version: 3.9 or higher
* Camera: Integrated or external webcam (720p recommended)
* Internet Connection: Required for OpenFoodFacts API

Installation:

Step 1 – Check Python Installation
Open terminal or command prompt:
python --version
Python 3.9 or higher is required.

Step 2 – Install Dependencies
Navigate to the project folder:
pip install -r requirements.txt
Required libraries:

* OpenCV – Image processing
* Pyzbar – Barcode detection
* Pillow – Image display
* Requests – API communication

Step 3 – Install ZBar Library

Windows:
pip install pyzbar

macOS:
brew install zbar

Linux:
sudo apt-get install libzbar0

Running the Application
Run the program:
python carboscan.py



Notes:

* An internet connection is required to retrieve product information.
* Some products may not be available in the OpenFoodFacts database.
* Detection performance depends on lighting conditions and camera quality.
