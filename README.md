# ⚡ Nexus Analytics Hub

A modern, interactive **business analytics dashboard** built using **Streamlit, Plotly, and Pandas**.  
Nexus Analytics Hub delivers executive-level insights, deep-dive analytics, and customer segmentation through a clean, dark-themed UI.

---
Live demo Link->https://nexusanalyticsapp-ijrsgzxajyp5xnzugngqjc.streamlit.app/

## 🚀 Features

### 📊 Executive Summary
- Total Revenue, Total Orders, Average Order Value (AOV), Active Customers
- Month-over-Month performance indicators
- Interactive revenue trend visualization
- Category-wise sales distribution (donut chart)

### 🧠 Deep Dive & Pareto Analysis
- Sales heatmap (Day vs Month) to uncover demand patterns
- Pareto (80/20 rule) analysis to identify top revenue-generating products
- Dual-axis charts for revenue and cumulative contribution

### 👥 Customer Segmentation (RFM Analysis)
- Recency, Frequency, Monetary (RFM) scoring
- Automatic customer segmentation:
  - Champions
  - Promising
  - At Risk
  - Lost
  - Standard
- Bubble chart for customer value matrix
- Exportable segmented customer data

### 📋 Data Exploration
- Interactive raw data table
- Year and date-range filtering
- CSV download support

---

## 🧪 Demo Data Engine
- Realistic synthetic sales data generator
- Seasonality and pricing noise simulation
- One-click demo data refresh
- Session-aware caching using Streamlit `session_state`

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit  
- **Visualization:** Plotly (Express & Graph Objects)  
- **Data Processing:** Pandas, NumPy  
- **Styling:** Custom CSS (Dark Theme)  
- **Language:** Python 3  

---

## 📂 Project Structure

.
├── app.py
├── README.md
└── requirements.txt

yaml
Copy code

---

## 📥 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/nexus-analytics-hub.git
cd nexus-analytics-hub
2. Install Dependencies
bash
Copy code
pip install -r requirements.txt
3. Run the Application
bash
Copy code
streamlit run app.py
📊 Supported CSV Format
Your dataset should contain the following columns:

Column Name	Description
OrderDate	Order date
CustomerID	Unique customer identifier
Category	Product category
ProductID	Product name or ID
Quantity	Units sold
TotalSales	Revenue generated

💡 Use Cases
Business and executive dashboards

Sales performance analysis

Customer segmentation and churn analysis

Product contribution and Pareto analysis

Resume-ready analytics project

🎨 UI Highlights
Modern dark-themed design

Responsive wide-layout dashboard

Interactive charts with zoom and hover

Clean KPI metric cards with deltas

Presentation-ready visuals

📤 Export Options
Download RFM-segmented customer data as CSV

Upload custom datasets for instant analysis

🧠 Future Enhancements
User authentication and access control

Database integration (PostgreSQL / BigQuery)

Sales forecasting and trend prediction

Cohort and retention analysis

Machine learning-based customer lifetime value (CLV)

