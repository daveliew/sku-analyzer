# SKU Performance Analyzer

A Streamlit web application for analyzing your top-performing products over the last 6 months.

## Features
- Interactive dashboard showing top SKU performance
- Revenue and quantity analysis
- Category performance breakdown
- Sales trends over time
- AI-powered insights and recommendations
- CSV export functionality

## Setup Instructions

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run sku_analyzer.py
```

The app will automatically open in your web browser at `http://localhost:8501`

## Usage
- The app comes with sample data to get you started
- Use the sidebar controls to adjust analysis parameters
- You can upload your own CSV file with columns: date, sku, product_name, quantity_sold, unit_price
- Export your analysis results as CSV files

## Requirements
- Python 3.7+
- See requirements.txt for package dependencies 