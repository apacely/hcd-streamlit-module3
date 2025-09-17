# HCD Interactive App (Streamlit) — Module 3

A small, schema‑aware Streamlit app that demonstrates **Human‑Centered Design (HCD)** by prioritizing clarity, low cognitive load, and immediate feedback. It’s pre‑tuned for the classic `insurance.csv` dataset (columns: `age`, `sex`, `bmi`, `children`, `smoker`, `region`, `charges`) but adapts to any CSV with categorical + numeric columns.

---

## ✨ What this app shows (HCD in practice)

- **Simple choices:** one categorical filter and one numeric range keep the UI easy to reason about.
- **Smart defaults:** auto‑selects useful columns (e.g., `smoker`, `charges`, `bmi`) when present.
- **Immediate feedback:** visualizations and **Insight Cards** update as you interact.
- **Progressive disclosure:** advanced stats live behind an expander to avoid overwhelming new users.

---

## 📁 Repository contents

```
app.py               # Streamlit app (v3, tuned for insurance.csv)
requirements.txt     # Minimal dependencies
README.md            # You are here
```

> Optional: add your dataset (e.g., `insurance.csv`) to the same folder for quick access when launching the app.

---

## 🚀 Quick start (TL;DR)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints (usually http://localhost:8501), then **Upload** your CSV or explore with any sample data you provide.

---

## 🧰 Setup (with virtual environment – recommended)

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Windows (PowerShell)
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

---

## 📊 Using the app

1. **Load data**: Click **Upload a CSV**. Headers must be on the first row.  
2. **Explore (filters)**  
   - *Category filter*: defaults to `smoker` → then `region` → then `sex` (if present).  
   - *Numeric range*: defaults to `charges` (with a trimmed 5–95% range to tame outliers), then `bmi`.  
3. **Visualize**  
   - **Scatter** *(default)*: `bmi` vs `charges`, color by `smoker`.  
   - **Bar**: aggregate mean/sum/median/count by a category (e.g., mean `charges` by `region`).  
   - **Histogram**: distribution of a numeric column (e.g., `bmi`).  
   - **Box**: numeric by category (e.g., `charges` by `smoker`).  
   - **Line**: time series if your data has a date column.  
4. **Insight Cards** (auto‑computed)  
   - Average charges (all, smokers, non‑smokers) with deltas.  
   - Median BMI & obesity rate (BMI ≥ 30).  
   - Mini bar chart: mean charges by region.  
5. **Descriptive stats**: Open the expander for a full `describe()` table.

> Works even if your dataset has different column names. If `smoker/region/sex/bmi/charges` are missing, the app chooses the first suitable columns automatically.

---

## 🧪 Tailoring to `insurance.csv`

The app is already optimized for this dataset. Useful views to include in your write‑up:

- **Scatter**: `bmi` (X) vs `charges` (Y), color `smoker`.  
- **Box**: `charges` by `smoker` (spot distribution differences).  
- **Bar (mean)**: `charges` by `region`.  
- **Histogram**: `bmi` with ~30 bins.

---

## 📝 Suggested reflection

**How I used ChatGPT:**  
ChatGPT helped me with fine-tuning the schema‑aware Streamlit app, offering suggestions to help reduce unnecessary features, change the columns and visualizations, set sensible defaults for `insurance.csv` (BMI vs Charges, color by smoker), and suggested Insight Cards to surface key comparisons immediately. GPT also helped me generate this README.md

**Why these interactions are HCD‑friendly:**  
A single category filter and one numeric range reduce cognitive load. Smart defaults provide immediate feedback without configuration. Multiple chart types let users try different “questions” rapidly—supporting iterative, user‑driven exploration.

**What I learned from the data:**  
Nothing much, really. This was mostly just for the assignment.

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push **`app.py`** and **`requirements.txt`** to a GitHub repo.  
2. Go to https://share.streamlit.io and connect your GitHub.  
3. Select the repo + branch, set **Main file path** to `app.py`.  
4. Deploy. You’ll get a URL you can submit with your assignment.

> No secrets or API keys are needed. The app runs entirely client‑side/server‑side in Streamlit with your uploaded CSV.
---

## 🧯 Troubleshooting

- **`ModuleNotFoundError: streamlit`** → run `pip install -r requirements.txt` (inside your venv).  
- **Nothing happens after upload** → ensure CSV has header row; check uncommon delimiters (try saving as standard comma‑separated CSV).  
- **No date chart option** → the app only enables time series if a column name includes “date” *or* parses as a datetime.  
- **Large CSV feels slow** → filter first, then visualize; consider sampling rows for exploration.  
- **Port in use** → `streamlit run app.py --server.port 8502` (change the port).

---

## 🔒 Data privacy

Your data stays local when running on your machine. If you deploy to Streamlit Cloud, any file you upload is processed by that service instance; avoid uploading sensitive data.

---

## 📜 License

Educational use for Module 3. Feel free to adapt for your course submission.
