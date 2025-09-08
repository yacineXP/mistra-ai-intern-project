# Mistralytics:  Chat With Your CSV (Powered by Mistral AI)
An interactive web app that lets you chat with your CSV files. Ask questions in plain English and get back data, charts, and insights, all powered by Mistral AI.

### ► Live Demo
▶️ [Watch the demo on YouTube](https://youtu.be/NRZIzo4MsxE) 

## ✨ Key Features
- **Natural Language Queries:** Ask complex questions about data using plain English, no coding required.

- **Asynchronous Processing:** Non-blocking API handles long-running analysis via background tasks without request timeouts.

- **Secure Code Execution:** AI-generated code runs in a secure, isolated sandbox to prevent vulnerabilities.

- **Multi-Modal Responses:** Intelligently detects and renders various result types:

  - **Tables** (pandas DataFrames)

  - **Single Values** (aggregations, counts, etc.)

  - **Plots & Charts** (generated with Matplotlib)

- **Intelligent Error Handling:** Gracefully handles invalid or nonsensical queries with clear user feedback.

- **Comprehensive Test Suite:** Unit and integration tests ensure code quality and reliability.

- **Containerized:** Fully containerized with Docker for easy, one-command setup.

- **Automated CI Pipeline:** GitHub Actions workflow automatically runs tests on every push to ensure stability.

## 🛠️ Tech Stack
- **Backend:**

  - **Framework:** FastAPI

  - **AI Model:** Mistral AI (mistral-large-latest)

  - **Data Handling:** Pandas

  - **Web Server:** Uvicorn & Gunicorn

  - **Security:** Python Subprocess Sandboxing

  - **Frontend:**

    - **Languages:** HTML, CSS, JavaScript (Vanilla)

    - **Styling:** Tailwind CSS

  - **Testing & CI/CD:**

    - **Framework:** Pytest, pytest-mock

    - **Automation:** GitHub Actions

    - **Deployment:**

    - **Containerization:** Docker

## 🚀 How to Run

**1. Clone the Repository**

```
git clone [https://github.com/yacineXP/mistra-ai-intern-project.git](https://github.com/yacineXP/mistra-ai-intern-project.git)
cd ai-data-analyst
```
**2. Set Up a Python Virtual Environment**

For macOS/Linux:
```
python3 -m venv venv
source venv/bin/activate
```
For Windows:
```
python -m venv venv
.\venv\Scripts\activate
```
**3. Install Dependencies**
```
pip install -r requirements-dev.txt
```
**4. Configure Environment Variables**
Create a .env file in the project root and add your Mistral AI API key.
```
MISTRAL_API_KEY="your_mistral_api_key_here"
```
**5. Build the Frontend**
This project uses a simple build step to compress the frontend files.
```
python3 build.py
```
**6. Run the Server**
Use Uvicorn for development with live reloading.
```
uvicorn app.main:app --reload
```
The application will be available at https://www.google.com/search?q=http://127.0.0.1:8000.

## 📄 API Documentation
The API is self-documenting via OpenAPI. Once running, access the interactive Swagger UI at:

https://www.google.com/search?q=http://127.0.0.1:8000/docs


