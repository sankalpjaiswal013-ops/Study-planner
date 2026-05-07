# 🧠 AI-Powered Study Planner

A comprehensive, full-featured Study Planner web application built completely in Python using **Streamlit**, **SQLite**, and **Google Gemini AI**.

This application acts as a personal tutor and organization hub, helping students track tasks, identify weak subjects, generate automated study timetables, and maintain focus using a built-in Pomodoro timer.

## 🚀 Features

* **Smart Dashboard**: Visualizes your 14-day study streak, weekly hours, and subject distribution using interactive Plotly charts.
* **Task & Subject Manager**: Add homework, exams, and general study tasks. The app automatically calculates a "Subject Score" (0-100) based on your completion rate and the difficulty of the tasks.
* **Weakness Analysis**: Automatically identifies your top 3 weak subjects and top 3 strong subjects, displaying them in a color-coded bar chart.
* **AI Chatbot Tutor**: Powered by Google Gemini 2.5 Flash. The chatbot reads your local database context (weak subjects, pending tasks) to give you hyper-personalized study advice and motivation.
* **Auto Timetable Generator**: Input your available hours, and the app generates a weekly study grid that automatically prioritizes your weakest subjects.
* **Pomodoro Timer**: A fully built-in ticking timer (Work, Short Break, Long Break) that logs your completed focus sessions directly into your daily study analytics.
* **Secure Local Database**: All data is stored locally in an SQLite database (`tasks.db`), ensuring privacy and speed.

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/study-planner.git
   cd study-planner
   ```

2. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a free Google Gemini API Key:**
   * Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and generate a free key.

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

5. **Configure the App:**
   * Open the app in your browser (usually `http://localhost:8501`).
   * Sign up for an account.
   * Go to the **Settings** page and paste your Google Gemini API key to activate the chatbot!

## 📦 Tech Stack
* **Frontend/Backend:** Streamlit (Python)
* **Database:** SQLite3
* **Charts:** Plotly Express
* **AI Integration:** Google Generative AI (Gemini)
* **Security:** bcrypt (Password Hashing)
