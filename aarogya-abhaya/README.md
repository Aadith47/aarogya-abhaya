# 🏥 Aarogya Abhaya

**A comprehensive healthcare monitoring web application** for tracking maternal health, newborn care, teenager wellness, and malnutrition detection.

## 📋 Features

- **Multi-role authentication** — ASHA workers, JPHA, LHA, pregnant women, teenagers, newborns (guardians)
- **Beneficiary registration & approval workflow** — ASHA → JPHA → LHA approval chain
- **Vaccination scheduler** — Automatic vaccination schedule generation for newborns
- **Video management** — ASHA workers can upload health education videos
- **Posture detection** — Real-time squat and sitting posture analysis for pregnant women (camera + ML)
- **Malnutrition detection** — AI-based image analysis for child malnutrition screening
- **Notice board** — ASHA workers can send notices to beneficiaries
- **Password reset** — Email OTP-based password recovery

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Node.js, Express.js |
| Database | PostgreSQL |
| ML Server | Flask, Streamlit, TensorFlow |
| Posture Detection | MediaPipe, OpenCV, YOLO, LSTM |
| Frontend | HTML, CSS, JavaScript |
| Email | Nodemailer (Gmail) |

## 📦 Prerequisites

- **Node.js** (v18 or later) — [Download](https://nodejs.org/)
- **Python** (v3.10 or later) — [Download](https://www.python.org/)
- **PostgreSQL** (v14 or later) — [Download](https://www.postgresql.org/download/)
- A **webcam** (for posture detection features)

## 🚀 Setup Instructions

### 1. Clone the repository
```bash
git clone <repo-url>
cd aarogya-abhaya
```

### 2. Set up the database
```bash
# Create the database
createdb aarogya_abhaya

# Run the schema file
psql -d aarogya_abhaya -f schema.sql
```
Or using pgAdmin:
1. Create a new database called `aarogya_abhaya`
2. Open the Query Tool and run the contents of `schema.sql`

### 3. Configure environment variables
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and fill in your values:
#   - DB_PASSWORD: your PostgreSQL password
#   - EMAIL_USER: your Gmail address
#   - EMAIL_PASS: your Gmail App Password (see below)
```

> **Gmail App Password:** Go to Google Account → Security → 2-Step Verification → App passwords → Generate one for "Mail".

### 4. Install Node.js dependencies
```bash
cd aarogya-backend
npm install
cd ..
```

### 5. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 6. Start the servers

**Option A: Start each server manually**

```bash
# Terminal 1 — Main website server (port 3000)
cd aarogya-backend
node server.js

# Terminal 2 — Flask ML redirect server (port 5000)
cd flask-ml-server
python app.py

# Terminal 3 — Malnutrition detection app (port 8501)
cd flask-ml-server
streamlit run malnutrition_app.py
```

**Option B: Use the start script (Windows only)**
```bash
# Edit start_servers.bat to fix paths for your system, then run:
start_servers.bat
```

### 7. Open in browser
```
http://localhost:3000
```

## 👥 Registration Codes

To register as a healthcare worker, use these codes:

| Role | Code |
|------|------|
| ASHA Worker | `ASHA-2026` |
| JPHA | `JPHA-2026` |
| LHA | `LHA-2026` |

> Beneficiaries (pregnant women, teenagers, newborns) are registered by ASHA workers and require JPHA + LHA approval before login.

## 📁 Project Structure

```
aarogya-abhaya/
├── .env.example          # Environment variable template
├── .gitignore            # Git ignore rules
├── schema.sql            # Database schema
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── db.js                 # Database connection module
├── package.json          # Root Node.js config
│
├── aarogya-backend/      # Main Express.js server
│   ├── server.js         # All API routes (1090+ lines)
│   ├── package.json      # Backend dependencies
│   └── public/           # Frontend files
│       ├── index.html    # Landing page
│       ├── login.html    # Login page
│       ├── register.html # Registration page
│       ├── asha_dashboard.html
│       ├── pregnant_dashboard.html
│       ├── teenager_dashboard.html
│       ├── newborn_dashboard.html
│       ├── jpha_dashboard.html
│       ├── lha_dashboard.html
│       ├── css/          # Stylesheets
│       └── js/           # Client-side scripts
│
├── flask-ml-server/      # ML prediction services
│   ├── app.py            # Flask redirect server
│   ├── malnutrition_app.py   # Streamlit malnutrition detector
│   └── malnutrition_model.h5 # Trained TensorFlow model
│
├── pregnant-module/      # Posture detection module
│   ├── run_all.py        # Camera API launcher
│   └── backend/
│       ├── camera_api.py
│       ├── camera_manager.py
│       ├── posture/      # Squat posture detection (LSTM)
│       ├── sitting_posture_module/  # Sitting posture (YOLO)
│       └── training/     # Training scripts & model
│
├── routes/               # Additional route files
│   ├── auth.js
│   └── asha.js
│
└── middleware/
    └── authMiddleware.js
```

## ⚠️ Notes

- The **posture detection** features require a webcam and open a separate OpenCV window.
- The **malnutrition model** (`malnutrition_model.h5`) is ~9 MB. If using Git LFS, add it with `git lfs track "*.h5"`.
- This is a **demo/academic project** — the AI predictions are not medical diagnostic tools.

## 📝 License

ISC
