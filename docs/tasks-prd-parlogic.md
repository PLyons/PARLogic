# ✅ PARLogic Task List (Updated)

---

## 🧱 Task Group 1: Project Initialization

- [x] Create GitHub repository `PARLogic` and clone locally  
  _Labels: setup, repo | Est. Effort: 15m_

- [x] Initialize root directory with `README.md`, `.gitignore`, and `LICENSE`  
  _Labels: setup | Est. Effort: 10m_

- [x] Scaffold project folders: `/frontend`, `/backend`, `/tests`, `/docs`  
  _Labels: setup | Est. Effort: 10m_

- [x] Set up Python virtual environment and `requirements.txt` in backend  
  _Labels: backend, setup | Est. Effort: 20m_

- [x] Initialize Node project in `/frontend` and install React  
  _Labels: setup, frontend | Est. Effort: 30m_

---

## 📥 Task Group 2: CSV Ingestion & Validation

- [ ] Design and implement `parse_csv()` method in `/backend/ingestion/parser.py`  
  _Labels: backend, data | Est. Effort: 30m_

- [ ] Add column validation and file error handling  
  _Labels: backend, validation | Est. Effort: 20m_

- [ ] Unit test `parse_csv()` with valid and invalid samples  
  _Labels: testing, backend | Est. Effort: 30m_

- [ ] Create test CSV input samples and place in `/tests/data`  
  _Labels: testing | Est. Effort: 10m_

---

## 📊 Task Group 3: Data Analysis & Recommendations

- [ ] Create analysis pipeline to calculate average monthly usage, max/min range  
  _Labels: backend, analysis | Est. Effort: 45m_

- [ ] Implement algorithm to suggest PAR levels and reorder points  
  _Labels: backend, algorithm | Est. Effort: 45m_

- [ ] Export results to CSV for user download  
  _Labels: backend, export | Est. Effort: 20m_

---

## 🌐 Task Group 4: Frontend UI & File Upload

- [ ] Implement file upload form in React  
  _Labels: frontend, ui | Est. Effort: 30m_

- [ ] Display parsed results and analysis in dashboard  
  _Labels: frontend, ui | Est. Effort: 60m_

- [ ] Add tooltips or inline help for key metrics  
  _Labels: frontend, ux | Est. Effort: 20m_

---

## ☁️ Task Group 5: Cloud Integration & Persistence

- [ ] Integrate Supabase for saving history and results  
  _Labels: cloud, backend | Est. Effort: 45m_

- [ ] Create queryable history UI in frontend  
  _Labels: frontend, cloud | Est. Effort: 45m_

---

## 🔁 Task Group 6: QA, Documentation & Deployment

- [ ] Write user guide in `/docs` with screenshots  
  _Labels: docs | Est. Effort: 60m_

- [ ] Add CI/CD pipeline for backend and frontend  
  _Labels: devops | Est. Effort: 60m_

- [ ] Deploy backend to Render/Fly.io  
  _Labels: deployment, backend | Est. Effort: 45m_

- [ ] Deploy frontend to Netlify/Vercel  
  _Labels: deployment, frontend | Est. Effort: 30m_