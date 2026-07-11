# Avocado Yield Advisor

First deployable prototype trained from `Master Avocado File for Chat GPT workbook(3).xlsm`.

## Model
- Selected: Extra Trees
- Training records: 3254
- Holdout MAE: 32.405 kg
- Holdout RMSE: 45.031 kg
- Holdout R²: 0.5
- Year excluded
- Sodium excluded
- Chloride included
- Sulfur treated as percent
- Missing values handled through median imputation plus missingness indicators

## Run locally
1. Install Python 3.11 or newer.
2. Open a terminal in this folder.
3. Run: `pip install -r requirements.txt`
4. Run: `streamlit run app.py`

## Deploy and obtain a shareable link
Upload this folder to a private GitHub repository, then connect it to Streamlit Community Cloud, Render, or another Python hosting service. Set `app.py` as the entry point.

## Important limitation
This is a research decision-support prototype. It finds patterns in the supplied historical data. It does not prove that changing a nutrient will cause the predicted yield change, and it should not replace local agronomic judgment.
