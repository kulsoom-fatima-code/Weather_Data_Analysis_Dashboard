# Historical Weather Data Analysis

A Python data-analysis project that explores historical UK weather records and presents the results in an interactive Streamlit dashboard.

## Dataset

Use the Kaggle dataset **Climate of England _ Professional Reforms.csv** from:
https://www.kaggle.com/code/ariohakhamanesh/analysis-of-uk-weather-dataset

Download the CSV from the Input section, rename it to exactly `weather_data.csv`, and place it in the same folder as `app.py`.

**Important:** The uploaded file supplied for project setup was a Jupyter notebook, not the CSV dataset. Therefore the ZIP does not contain the actual data file. Add `weather_data.csv` before running the notebook or dashboard.

## Project files

- `weather_analysis.ipynb` — data inspection, cleaning, duplicate checks, outlier analysis, univariate and bivariate analysis, and written findings.
- `app.py` — interactive Streamlit dashboard with date/category filters, metrics, charts, correlation heatmap, findings and raw-data toggle.
- `requirements.txt` — Python dependencies.
- `.gitignore` — excludes virtual environments and secrets.

## Research questions

1. What is the distribution and spread of temperature?
2. How is humidity distributed?
3. What is the distribution of wind speed?
4. Is temperature associated with humidity?
5. Is wind speed associated with humidity?

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open `weather_analysis.ipynb` in VS Code or Jupyter and run cells from top to bottom.

## Deployment

1. Push the project folder to a public GitHub repository.
2. Ensure `weather_data.csv` is included if it is under the GitHub size limit (50 MB for this assignment).
3. Open https://share.streamlit.io/
4. Deploy the repository using `app.py` as the main file.
5. Test date/category filters, charts and raw-data checkbox.

## Findings and live app

Complete the three key findings and add the deployed Streamlit URL here after running the notebook and deploying the app. Do not invent findings before analyzing the actual CSV.
