# SmartPharma Stock Management

![AI-Powered](https://img.shields.io/badge/AI-Powered-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0-ff69b4)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0.0-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13.0-blue)
![Pandas](https://img.shields.io/badge/Pandas-1.3.0-150458)
![Altair](https://img.shields.io/badge/Altair-4.1.0-yellow)
![Plotly](https://img.shields.io/badge/Plotly-5.3.1-3F4F75)

## 📋Project Summary
SmartPharma Stock Management is a cutting-edge **AI-powered Pharmaceutical Warehouse Management System** designed to 
revolutionize medication management, pharmacy operations, and order processing. Using advanced machine learning 
algorithms, artificial intelligence, and data visualization techniques, this system goes beyond traditional CRUD 
functionality to deliver predictive analytics and intelligent insights.


### 🤖AI-Driven Features

1. **Optimal Stock Prediction with Machine Learning**
   - Predicts optimal medication stock level using historical data
   - Uses advanced ML models: XGBoost and Random Forest
   - Enhances inventory management with data-driven forecasting

2. **Advanced Medication Analysis powered by Anthropic AI**
   - Conducts comprehensive analysis of medication images using cutting-edge AI technology
   - Identifies active substance, and therapeutic properties
   - Suggests intelligent alternatives based on active ingredients
   - Enhances decision-making processes

3. **Intelligent Supplier Recommendations**
   - Automatically generates a list of top-performing Romanian medications suppliers
   - Provides data-driven insights to optimize supply chain efficiency and resilience

4. **AI Web Scraping**
   - Keeps the system up-to-date with the latest ANMDMR announcements
   - Employs intelligent parsing of regulatory updates
   - Ensures compliance and timely adaptation to industry changes

### 📈 Data Visualization and Analysis
- **Interactive Charts with Altair and Plotly**
  - Visualize stock trends, sales patterns, and predictive analytics
  - Create dynamic and responsive charts for better data interpretation
  - Enhance user experience with interactive data exploration

- **Efficient Data Manipulation with Pandas**
  - Process and analyze medications dataset information
  - Perform complex data transformations and statistical analyses
  - Integrate seamlessly with ML models and visualization libraries

## 🚀 Key Features
- **Advanced CRUD Operations**: Manage medications, pharmacies, and orders.
- **Predictive Analytics**: AI-powered predictions of stock levels for better inventory management.
- **AI-Driven Medication Analysis**: Detailed information about ingredients and smart alternative suggestions.
- **Supplier Insights**: A curated list of top suppliers created by AI for strategic partnerships.
- **Regulatory Compliance**: Automated collection of information on the latest industry announcements.
- **User-Friendly Interface**: An intuitive Streamlit-based frontend for specific views and functionalities.
- **Data Visualization**: Interactive charts and graphs using Altair and Plotly.
- **Robust Data Processing**: Efficient handling of large-scale data with Pandas and seamless integration with AI/ML 
models.

## 🛠 Tech Stack
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **AI & Machine Learning**:
  - XGBoost and Random Forest for predictive modeling
  - Anthropic AI integration for advanced medication analysis
- **Web Scraping**: BeautifulSoup for intelligent data extraction
- **Data Processing**: Pandas for efficient data manipulation and analysis
- **Data Visualization**:
  - Altair for declarative statistical visualizations
  - Plotly for graphs

## 🔧 Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Roxana-Calinov/my_pharma_repo.git
2. Install Dependencies
    ```bash
    pip install -r requirements.txt
3. Set Up PostgreSQL Database 
- Make sure you have PostgreSQL installed on your machine
- Create a new DB for the project and configure it.

4. Start the FastAPI
    ```bash
    uvicorn main:app --reload
5. Access the Streamlit Frontend
    ```bash
   streamlit run app.py
6. Open Your Browser:
    ```bash
   Access the Streamlit app at http://localhost:8501 and the FastAPI at http://localhost:8000

Powered by AI 🤖 | Engineered for Efficiency 🚀 | Designed for the Future of Pharmacy 💊