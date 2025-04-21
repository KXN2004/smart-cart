# Smart Cart

Smart Cart is an IoT-based project designed to streamline the shopping experience by automating the cart checkout process. It uses RFID technology to detect items added to or removed from the cart and communicates with a backend server to manage the cart's contents and generate invoices.

## Features

- **RFID Integration**: Detects items using RFID tags.
- **WiFi Connectivity**: Communicates with the backend server via WiFi.
- **Dynamic Cart Management**: Automatically updates the cart's contents in real-time.
- **Invoice Generation**: Displays and calculates the total cost, including GST.
- **QR Code Payment**: Generates a QR code for easy checkout and payment.
- **Error Handling**: Handles invalid cart IDs and missing items gracefully.

## Components

### Hardware
- **ESP8266**: Microcontroller for WiFi connectivity.
- **MFRC522**: RFID reader for detecting items.
- **RFID Tags**: Attached to items for identification.

### Software
- **Backend**: Built using FastAPI for managing cart data and generating invoices.
- **Frontend**: HTML templates styled with CSS for user interaction.
- **Database**: SQLite for storing cart and item data.

## How It Works

1. **Item Detection**: 
   - The RFID reader detects items added to or removed from the cart.
   - The ESP8266 sends the item ID and cart ID to the backend server via a POST request.

2. **Backend Processing**:
   - The server updates the cart's contents in the database.
   - It calculates the total cost, including GST, and generates an invoice.

3. **User Interaction**:
   - Users can view their cart, checkout, and pay using a QR code.
   - Invalid cart IDs or errors are displayed with appropriate messages.

## Setup Instructions

### Hardware Setup
1. Connect the MFRC522 RFID reader to the ESP8266 as per the pin configuration.
2. Power the ESP8266 and ensure it is connected to a WiFi network.

### Software Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/kxn2004/smart-cart.git
   cd smart-cart