# Movie Recommendation System

This is a **Movie Recommendation System** built using **FastAPI (Backend)** and **Next.js (Frontend)**. It provides movie recommendations based on user preferences and various algorithms.

## 🛠️ Setup Instructions

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/mahesh-bhosale/movie-recommendation-system.git
cd movie-recommendation-system
```

---

## 🚀 Backend Setup (FastAPI)

### 📌 Create a Virtual Environment
```sh
cd backend
python -m venv venv
```

### 📌 Activate Virtual Environment
#### 🖥️ Windows (PowerShell)
```sh
venv\Scripts\activate
```
#### 🐧 Linux / macOS
```sh
source venv/bin/activate
```
#### Store the Required .pkl Files

Download or move the following .pkl files into backend/app/ml_model/:

simi.pkl (Similarity matrix for movie recommendations)

movie_dict.pkl (Preprocessed movie data dictionary)

Ensure these files exist before running the backend.
### 📌 Install Dependencies
```sh
pip install -r requirements.txt
```

### 📌 Run the FastAPI Server
```sh
uvicorn app.main:app --reload
```
> The API will be available at: **http://127.0.0.1:8000**

---

## 🌐 Frontend Setup (Next.js)

### 📌 Navigate to `frontend/` Folder
```sh
cd ../frontend
```

### 📌 Install Dependencies
```sh
npm install
```

### 📌 Set Environment Variables
Create a `.env.local` file in the `frontend` folder:
```sh
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local
```

### 📌 Run the Frontend
```sh
npm run dev
```
> The frontend will be available at: **http://localhost:3000**

---

## 🎯 Project Structure
```
movie-recommendation-system/
│── backend/          # FastAPI backend
│── frontend/         # Next.js frontend
│── README.md         # Project documentation
│── .gitignore        # Git ignore file
```

---

## 🔥 Features
- Movie recommendations based on user preferences
- Modern UI with **Next.js & Tailwind CSS**
- FastAPI backend for handling API requests
- Docker setup for deployment (**Coming Soon**)

---

## 🏆 Contributors
- **Mahesh Bhosale** ([GitHub](https://github.com/mahesh-bhosale))

---

