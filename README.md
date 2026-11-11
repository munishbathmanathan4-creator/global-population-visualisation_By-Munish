# Global Population Growth and Distribution — JIE42403

## Project structure
- `app.py` — Streamlit application with 3 objective pages and 9 visualizations.
- `requirements.txt` — Python packages.
- `report_template.md` — report structure to complete after running the app.

## Dataset
Our World in Data, **Population 1950–2023**, processed from United Nations World Population Prospects 2024.
Dataset page: https://ourworldindata.org/grapher/population-unwpp
CSV is loaded by the app from the dataset's published CSV endpoint.

## Step-by-step setup in Visual Studio Code (Windows)
1. Install Python 3.10 or newer from https://www.python.org/downloads/. During installation, tick **Add Python to PATH**.
2. Install Visual Studio Code from https://code.visualstudio.com/.
3. Create a folder named `global_population_visualisation`.
4. Copy `app.py`, `requirements.txt`, and `report_template.md` into that folder.
5. Open the folder in VS Code: **File → Open Folder**.
6. Open **Terminal → New Terminal**.
7. Create a virtual environment:
   - Windows: `py -m venv .venv`
8. Activate it:
   - PowerShell: `.\.venv\Scripts\Activate.ps1`
   - If PowerShell blocks activation, use Command Prompt terminal and run: `.venv\Scripts\activate.bat`
9. Install packages: `python -m pip install -r requirements.txt`
10. Run the app: `python -m streamlit run app.py`
11. A browser tab should open. If not, copy the local URL printed in the terminal (usually `http://localhost:8501`).
12. Check all three tabs, test the year selector, and capture clear screenshots for your report.
13. To stop the app, return to the terminal and press `Ctrl+C`.

## Notes
- An internet connection is required because the app reads the CSV from Our World in Data.
- The dataset currently covers 1950–2023. The dashboard detects the actual first and last years available.
- Review every chart and replace the report template's prompts with interpretations supported by your actual results.
- For public deployment, create a GitHub repository containing `app.py` and `requirements.txt`, then deploy it using Streamlit Community Cloud: https://share.streamlit.io/
