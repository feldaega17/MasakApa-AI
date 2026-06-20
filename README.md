# MasakApa AI 🍳

**MasakApa AI** adalah aplikasi web pintar berbasis AI (Sistem Rekomendasi) yang membantu Anda menemukan ide masakan berdasarkan sisa bahan yang tersedia di kulkas Anda. Proyek ini dikembangkan sebagai Capstone Project Tema: *AI for Smart Recommendation Systems* (Pijak & IBM SkillsBuild).

## ✨ Fitur Utama
- **Rekomendasi Cerdas (Content-Based Filtering):** Menyajikan 5 resep paling relevan dari ~15.000 resep masakan Indonesia menggunakan algoritma **TF-IDF** dan **Cosine Similarity**.
- **Filter & Sortir:** Menyaring resep berdasarkan kategori masakan atau mengurutkannya berdasarkan tingkat kepraktisan (jumlah langkah paling sedikit).
- **Pencocokan Bahan:** Menampilkan secara rinci *Bahan Tersedia* (irisan kata) dan *Bahan Kurang* untuk setiap rekomendasi.
- **Antarmuka Premium:** Desain UI/UX modern bergaya *glassmorphism* yang sangat elegan, *responsive*, dan terintegrasi langsung dengan API backend.

## ⚙️ Arsitektur Sistem
- **Frontend:** HTML5, Tailwind CSS, Vanilla JS.
- **Backend:** Python, FastAPI, Uvicorn, Pandas, Scikit-learn, Joblib.
- **Dataset:** Indonesian Food Recipes (14.945 resep yang telah di-*cleaning*).

---

## 🚀 Cara Menjalankan Project (Local Development)

Ikuti langkah-langkah di bawah ini untuk menjalankan aplikasi MasakApa AI di komputer Anda setelah melakukan *clone* repository:

### 1. Clone Repository
```bash
git clone https://github.com/username-anda/MasakKita.git
cd MasakKita
```

### 2. Siapkan Environment & Dependencies
Sangat disarankan menggunakan *virtual environment*.
```bash
# Membuat virtual environment
python -m venv venv

# Aktivasi virtual environment (Mac/Linux)
source venv/bin/activate
# Aktivasi virtual environment (Windows)
# venv\Scripts\activate

# Install semua library yang dibutuhkan
pip install -r backend/requirements.txt
```

### 3. Pastikan Model Telah Tersedia (Ekspor dari Notebook)
Sistem membaca model `.pkl` (TF-IDF Vectorizer & Matrix) yang diekstrak dari Jupyter Notebook. Pastikan folder `models/` sudah terisi dengan menjalankan *notebook* `notebooks/01_EDA_and_Modeling.ipynb` atau eksekusi secara CLI via terminal:
```bash
jupyter nbconvert --execute --inplace notebooks/01_EDA_and_Modeling.ipynb
```
*(Catatan: Jika folder `models/` belum ada, API backend akan secara otomatis melakukan "training on the fly" saat server dijalankan pertama kali, namun direkomendasikan menggunakan file model agar respons *server* instan).*

### 4. Jalankan Aplikasi
Karena *frontend* dan *backend* sudah terintegrasi rapi dalam **satu server FastAPI**, Anda cukup menjalankan *satu* perintah dari *root directory* proyek:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Akses Aplikasi
Buka *browser* web Anda dan kunjungi:
👉 **[http://localhost:8000/](http://localhost:8000/)**

Anda akan langsung disambut oleh tampilan antar muka MasakApa AI. 
(Untuk melihat dokumentasi API Swagger UI, Anda bisa mengunjungi `http://localhost:8000/docs`).

---

## 📖 Contoh API Endpoint
Aplikasi ini melayani request pada endpoint utama: **POST `/recommend`**

**Contoh Payload Request:**
```json
{
  "ingredients": "ayam, cabai, telur",
  "category": "Sayur",
  "sort_by": "practicality"
}
```

**Keterangan Parameter:**
- `ingredients`: (String) Bahan yang Anda miliki dipisahkan koma.
- `category`: (Opsional) Filter teks pencarian ke dalam kategori masakan.
- `sort_by`: (Opsional) `relevance` untuk paling relevan, atau `practicality` untuk merekomendasikan resep dengan jumlah langkah tersedikit.
