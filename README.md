
## Overview

---

## 📁 Project Structure


## 🚀 Quick Start (Reproducibility: ≤2 Commands)

## 📊 Usage Examples

### 1. Train the Forecaster
```bash
python src/forecaster.py --train --data dataset/grid_history.csv
# Output: Saves lgbm_classifier.pkl and lgbm_regressor.pkl to ./model/
```

### 2. Generate Predictions for 24 Hours
```bash
python src/forecaster.py --predict --data dataset/recent_24h.csv
# Output: JSON with hourly P(outage) and E[duration | outage]
```

### 3. Generate Appliance Schedule

### 4. View the Dashboard
```bash
python -m http.server 8000 --directory .
# Open browser to http://localhost:8000/lite_ui.html
```


## 🔧 Technical Notes


## 📄 License & Submission

This project is submitted as-is for hackathon evaluation. See [SIGNED.md](SIGNED.md) for honor code.
