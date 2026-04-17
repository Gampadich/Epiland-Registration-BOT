# Epiland Booking Automation Bot

## Project Overview
This project is an intelligent Telegram bot designed to automate the registration and booking process for Epiland entertainment centers. The system leverages Large Language Models (LLM) to process natural language inputs and utilizes headless browser automation to interact with the official web interface.

## Core Features
- **Natural Language Data Extraction:** Uses Google Gemini 2.0 Flash to parse unstructured user messages into structured JSON data (Name, Phone, City, Date).
- **Persistent User Storage:** Implements an SQLite-based database layer to store and retrieve user profiles, enabling a seamless return-user experience.
- **Web Automation Engine:** Employs Playwright to execute automated form filling on the client’s website, eliminating manual data entry.
- **Asynchronous Processing:** Built on the Aiogram 3.x framework with multi-threaded execution for browser tasks to ensure high availability and responsiveness.

## Technical Architecture
The system is divided into five main modules:
1. **Bot Interface (telegramBOT.py):** Manages the communication lifecycle and user interaction.
2. **Intelligence Layer (AI.py):** Interfaces with the Gemini API for intent recognition and data structuring.
3. **Data Access Object (database.py):** Handles CRUD operations for user records within a local SQLite instance.
4. **Automation Script (automation.py):** Controls the Chromium browser instance to perform end-to-end web registration.
5. **Configuration (URLS.py):** Manages mapping between physical locations and their respective web endpoints.

## Tech Stack
- **Language:** Python 3.14
- **Frameworks:** Aiogram 3.x, Playwright
- **AI Integration:** Google Generative AI (Gemini API)
- **Database:** SQLite3
- **Concurrency:** Asyncio, ThreadPoolExecutor

## Installation and Deployment
1. Clone the repository to your local machine.
2. Install the required dependencies:
   ```bash
   pip install aiogram google-genai playwright
   playwright install chromium
Set up your environment variables (Telegram Bot Token and Google API Key).

Initialize the database and launch the bot:

Bash
python telegramBOT.py
Workflow Logic
User provides booking information in free-form text.

AI parses the text; if information is missing, the bot asks clarifying questions.

Once data is complete, the user confirms the details via an inline keyboard.

The bot triggers a background process that launches a browser, navigates to the specific branch URL, and submits the form.

A confirmation notification is sent back to the user upon successful completion.