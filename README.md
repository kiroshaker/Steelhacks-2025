# Steelhacks-2025

RxCast is a full-stack application built for **Steelhacks 2025**.  

It predicts pharmacy medication demand using machine learning models and provides a **Next.js/ReactJS** frontend for visualization and inventory management.


- **Predictive Analytics**: Uses machine learning (XGBoost) to forecast demand for medications.  
- **Inventory Tracking**: Frontend displays current stock, lead times, risks, and suggested purchase orders.  
- **Interactive Dashboard**: Built with Next.js + ReactJS for real-time updates.  
- **Data Sources**: Weather + pharmacy datasets integrated into demand models.

**Instructions on how to run it**:
### 1. Clone the repo
```
git clone https://github.com/kiroshaker/Steelhacks-2025.git
cd Steelhacks-2025
```

**2. Backend setup (Python)**
```
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

**3. Frontend setup (Next.js):**
```
pip install -r requirements.txt
python rxcast_demand_forecast_xgb.py

cd rxcast-frontend
npm install
npm run dev
```
