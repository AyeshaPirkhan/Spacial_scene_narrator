# Spacial Scene Narrator ♿

**An AI-powered assistive vision system that helps visually impaired users understand their surroundings through voice-based scene descriptions, object detection, text reading, and navigation guidance.**

## 🌟 Overview

Spacial Scene Narrator is a Python-based assistive technology prototype designed to help visually impaired users perceive and understand their environment using computer vision and AI.

The system analyzes camera input, identifies objects and surroundings, reads visible text, and provides spoken feedback. It also offers navigation-related guidance to help users understand nearby obstacles and their surroundings.

The heavy AI processing currently runs on a computer, while a mobile device can connect as a client through the application's HTTP endpoints.

## ✨ Features

- **Scene Understanding:** Analyzes the camera view to describe the user's surroundings.
- **Object Detection:** Uses YOLO-based computer vision to identify objects in the environment.
- **Detailed Scene Analysis:** Uses Florence-2 and Gemini for richer visual descriptions and contextual understanding.
- **OCR and Text Reading:** Extracts visible text using OCR services and text-recognition tools.
- **Voice Feedback:** Converts analysis results into speech using text-to-speech functionality.
- **Voice-Based Interaction:** Supports speech recognition and command-based interaction.
- **Navigation Assistance:** Integrates navigation-related reasoning into scene analysis to provide contextual guidance.
- **Mobile Connectivity:** Provides HTTP endpoints through a Flask-based server so a mobile client can communicate with the backend.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| OpenCV | Camera input and image processing |
| YOLO / YOLO-World | Object detection and identification |
| Florence-2 | Detailed image captioning |
| Gemini API | On-demand visual and contextual analysis |
| OCR.Space / Tesseract | Text extraction |
| Flask | Web endpoints and mobile connectivity |
| SpeechRecognition | Voice command input |
| pyttsx3 | Text-to-speech output |

## 🏗️ System Architecture

1. **Input:** Capture camera frames or images.
2. **Processing:** Analyze visual input using object detection and image-understanding models.
3. **Text Recognition:** Extract text when the user requests text-reading functionality.
4. **Reasoning:** Interpret the scene and generate relevant descriptions or navigation-related guidance.
5. **Audio Output:** Convert the generated information into spoken feedback.
6. **Mobile Communication:** Allow a connected mobile client to interact with the computer-hosted backend.

## 🎙️ Interaction Controls

The prototype supports the following keyboard-style controls:

| Input | Action |
|---|---|
| Press `1` | Scene and object analysis |
| Press `2` | OCR and text reading |
| Press `3` | Detailed AI-based scene analysis |
| Hold the exit control for approximately 5 seconds | Exit the application |

*Controls may depend on the active application interface and configuration.*

## 📁 Project Structure

```text
Spacial_scene_narrator/
├── models/
├── services/
├── static/
├── templates/
├── uploads/
├── outputs/
├── utils/
├── weights/
├── app.py
├── camera.py
├── config.py
├── mobile_server.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

*Some folders are created or populated at runtime. Model weights and local environment files should not be committed to GitHub.*

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or another version compatible with the project's dependencies
- Git
- A working camera if using live camera features
- API credentials for external services used by your configuration

### 1. Clone the repository

```bash
git clone https://github.com/AyeshaPirkhan/Spacial_scene_narrator.git
cd Spacial_scene_narrator
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and add your own API credentials.

```env
GEMINI_API_KEY=your_gemini_api_key
OCR_SPACE_API_KEY=your_ocr_space_api_key
```

Keep `.env` private. Never commit real API keys, passwords, or access tokens to GitHub.

### 5. Download required model weights

Download the model weights required by your implementation and place them in the locations expected by the project. Large model files are excluded from version control.

Check the model paths in the configuration and service files before running the application.

### 6. Run the application

The project contains multiple entry points. Depending on which feature you want to run, start the relevant script:

```bash
python camera.py
```

For the Flask application, use:

```bash
python app.py
```

For mobile HTTP connectivity, use:

```bash
python mobile_server.py
```

*Run the entry point appropriate to your setup. These commands are not necessarily intended to run simultaneously, and additional configuration may be required.*

## 🔐 Security and Privacy

- Store API credentials in environment variables or a local `.env` file.
- Keep `.env`, model weights, generated outputs, and private uploads out of version control.
- Avoid publishing private images or other sensitive user data.
- Use authenticated and appropriately secured endpoints before exposing the backend beyond a trusted local network.
- Treat AI-generated descriptions and navigation guidance as assistance, not a substitute for a mobility aid or professional orientation-and-mobility training.

## 🚧 Current Scope and Future Improvements

This project is a prototype, and its capabilities depend on the models, camera setup, network connection, and external APIs available.

Potential improvements include:

- Improving low-latency scene analysis.
- Strengthening obstacle and path-awareness capabilities.
- Enhancing offline processing and reducing dependence on external APIs.
- Improving mobile usability and accessibility.
- Adding robust error handling and evaluation across different lighting and environmental conditions.
- Improving privacy, authentication, and secure communication between the mobile client and backend.

## 🎯 Project Goal

The goal of Spacial Scene Narrator is to make visual information more accessible by translating the surrounding environment into useful spoken descriptions, helping visually impaired users gain additional awareness of the world around them.

## 👩‍💻 Author

**Ayesha Pirkhan**

GitHub: [AyeshaPirkhan](https://github.com/AyeshaPirkhan)

---

*Built as an assistive computer-vision and AI prototype focused on accessibility.*
