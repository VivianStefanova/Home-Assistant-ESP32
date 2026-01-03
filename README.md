# Home Chatbot for Voice Control with Local LLM (Home Assistant Robot)

A privacy-focused, offline voice assistant capable of controlling smart home actuators (LEDs) using a local Large Language Model (LLM). This project simulates the functionality of assistants like Alexa or Siri but runs entirely on a local server without internet dependency.

## 📋 Overview

The goal of this project is to create a robotic system that processes voice commands to control hardware components (such as an LED) and engages in natural conversation. Unlike commercial alternatives, this system ensures privacy by processing all data locally on a home machine using a custom server.

**Key Features:**
* **Fully Local:** No internet connection required; uses a local server for AI processing.
* **Push-to-Talk:** Physical button activation to ensure privacy and precise command timing.
* **Voice Actuation:** Recognizes specific voice commands to control an RGB LED.
* **Real-time Streaming:** Uses UDP protocol for low-latency audio transmission.

## 🛠️ Hardware Requirements

The project is built using affordable components available from AliExpress. The total budget is approximately **41.44 BGN**.

| Component | Model / Specs | Price (approx) |
| :--- | :--- | :--- |
| **Microcontroller** | ESP32-DevKit-LiPo (Olimex) | 14.15 BGN |
| **Microphone** | INMP441 Omnidirectional I2S | 5.88 BGN |
| **Amplifier** | MAX98357A Digital I2S Amplifier | 4.30 BGN |
| **Speaker** | 4 Ohm 3W Speaker | 7.03 BGN |
| **Input** | Tactile Push Button | 0.24 BGN |
| **Output** | Multicolor RGB LED | 0.30 BGN |
| **Misc** | Breadboard & Jumper Wires | ~9.50 BGN |

## 💻 Software Architecture

The system consists of two main parts: the **Client** (ESP32) and the **Server** (PC).

### 1. Client (ESP32)
* **Language:** C++ (Arduino Framework).
* **Functionality:**
    * Connects to WiFi.
    * Records audio via I2S microphone when the button is pressed.
    * Streams audio to the server via UDP.
    * Receives response audio and commands from the server.
    * Plays audio via I2S amplifier and updates LED status.
* **Key Source File:** `esp32_code/src/main.cpp`.

### 2. Server (PC)
* **Language:** Python.
* **AI Stack:**
    * **STT (Speech-to-Text):** OpenAI Whisper (Local `base` model) via `faster-whisper`.
    * **LLM (Brain):** Llama 3.2 running on **Ollama**.
    * **TTS (Text-to-Speech):** Piper TTS (Voice: `en_US-lessac-low.onnx`).
* **Functionality:** Listens for UDP packets, transcribes audio, queries Llama 3.2 for a response/command, generates speech, and streams it back to the client.

## 🗣️ Supported Commands

The assistant listens for specific keywords to control the onboard LED.

* `LED ON` - Turns the light **White**.
* `LED OFF` - Turns the light **Off**.
* `LED R` - Turns the light **Red**.
* `LED G` - Turns the light **Green**.
* `LED B` - Turns the light **Blue**.

## 🚀 Installation & Setup

### Prerequisites
* **Hardware:** Assemble the circuit connecting the INMP441, MAX98357A, Button, and LED to the ESP32 pins defined in `main.cpp` (Blue: 18, Green: 17, Red: 16, Button: 32).
* **Software:** Python 3.x and installed on your server machine.

### Server Setup
1.  Install **Ollama** and pull the Llama 3.2 model:
    ```bash
    $ ollama pull llama3.2
    ```
2.  Install Python dependencies:
    ```bash
    $ cd server
    $ pip install -r requirements.txt
    ```
3.  Run the server:
    ```bash
    $ python main.py
    ```
    *Note: The server listens on port `5005` by default.*

### Client Setup
1.  Open the project in **PlatformIO** or **Arduino IDE**.
2.  Modify `src/main.cpp` with your WiFi credentials and Server IP:
    ```cpp
    const char* ssid = "YourWiFiName";
    const char* password = "YourPassword";
    IPAddress serverIP(192, 168, 1, 100); // Change to your PC's IP
    ```
3.  Upload the code to the ESP32.

## 🕹️ Usage
1.  Ensure the Python server is running.
2.  Power on the ESP32. Wait for the "WiFi connected" message in Serial Monitor.
3.  **Push-to-Talk:** Press and hold the button to speak.
    * *Example:* "Turn the light red".
4.  Release the button to send the audio.
5.  The assistant will process your request, change the LED color (if a command was heard), and reply via the speaker.

## 👥 Authors
* **Vivian Rosenova Stefanova**
* **Viktor Viktorov Pazhev**

*Sofia University "St. Kliment Ohridski", Faculty of Mathematics and Informatics*.