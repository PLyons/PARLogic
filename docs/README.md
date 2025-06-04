# PARLogic

PARLogic is an open-source, cloud-compatible inventory analysis and PAR-level optimization platform designed specifically for hospital supply chain teams. It enables data-driven purchasing decisions through CSV ingestion, usage pattern analysis, PAR level recommendations, and intuitive reporting dashboards.

---

## 📦 Key Features

- 📁 Upload & analyze CSV purchase order history
- 📊 Auto-calculate PAR levels based on historical trends
- 🧮 Statistical usage metrics (monthly, weekly, daily)
- 💡 Reorder recommendations with cost projections
- 📈 Visual dashboards and exportable reports
- ☁️ Supabase/PostgreSQL cloud integration
- 🧪 CI/CD-ready and fully testable backend
- 🔐 Scalable, modular architecture for long-term growth

---

## 🛠 Tech Stack

| Layer      | Technology         |
|------------|--------------------|
| Frontend   | React + Vite       |
| Backend    | Python (pandas)    |
| Storage    | Supabase (PostgreSQL) |
| Hosting    | Netlify, Render (planned) |
| DevOps     | GitHub + CI/CD     |

---

## 🗂 Project Structure

```
PARLogic/
├── backend/            # Python ingestion and analytics engine
│   ├── ingestion/      # CSV parsing and validation logic
│   └── analysis/       # Usage analysis, PAR calculations
├── frontend/           # React app for file upload and display
├── tests/              # Unit and integration tests
├── docs/               # Documentation and user guides
├── .gitignore
├── README.md
└── LICENSE
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/PLyons/PARLogic.git
cd PARLogic
```

### 2. Set up Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173/` to see the app in action.

---

## 📄 Documentation

- [Product Requirements (PRD)](./docs/prd-parlogic.md)
- [Task List](./tasks-prd-parlogic.mdc)
- [System Design Overview](./docs/system-design.md) *(coming soon)*

---

## 🧑‍💻 Contributing

Pull requests and issues are welcome. For major changes, open a discussion first. Please make sure to update tests as appropriate.

---

## 📜 License

This project is licensed under the MIT License.