# **Preprocessing & Exploratory Data Analysis (EDA) Project**

## **📌 Project Overview**

This project performs data preprocessing and exploratory data analysis (EDA) for weather and solar radiation datasets. It includes:
* Data cleaning and interpolation.
* Solar geometry feature generation using pvlib.
* Temporal feature extraction (Hour, Day, Month, Year, DOY).
* Hourly resampling of time-series data.
* A comprehensive set of visualizations:
  1. Standard Line Graphs
  2. Monthly Faceted Line Plots (Raw Hourly)
  3. Monthly Faceted Line Plots (Daily Aggregated)
  4. Data Distribution Histograms
  5. Spearman Correlation Heatmap
  6. Scatter Plots of sr_avg vs other variables


## **⚙️ How to Run**

### **1️⃣ Install Dependencies**
pip install pandas numpy matplotlib seaborn pvlib scipy

### **2️⃣ Prepare the Dataset**
* Place your dataset (Excel format) inside the `data`/ folder.
* Ensure the datetime column is named Time and formatted as %d/%m/%Y %H:%M:%S.

### **3️⃣ Run the Script**
`python [01]_preprocessing_and_eda.py`
