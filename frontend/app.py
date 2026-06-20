import streamlit as st
import requests
import os

# Backend API URL (use localhost for MVP)
API_URL = os.getenv("API_URL", "http://localhost:8000/recommend")

st.set_page_config(page_title="MasakApa AI", layout="centered", page_icon="🍳")

st.title("MasakApa AI")
st.write("Temukan ide masakan berdasarkan bahan yang tersedia.")

ingredients_input = st.text_area(
    "Masukkan bahan yang Anda miliki (pisahkan dengan koma):", 
    placeholder="ayam, bawang putih, cabai"
)

if st.button("Cari Resep", type="primary"):
    if not ingredients_input.strip():
        st.warning("Mohon masukkan setidaknya satu bahan.")
    else:
        with st.spinner("Mencari resep terbaik untuk Anda..."):
            try:
                response = requests.post(API_URL, json={"ingredients": ingredients_input})
                
                if response.status_code == 200:
                    data = response.json()
                    recommendations = data.get("recommendations", [])
                    
                    if not recommendations:
                        st.info("Maaf, tidak ditemukan resep yang cocok dengan bahan tersebut.")
                    else:
                        st.success(f"Ditemukan {len(recommendations)} rekomendasi resep!")
                        
                        for idx, rec in enumerate(recommendations, 1):
                            st.subheader(f"{idx}. {rec['title']}")
                            
                            score_percent = int(rec['similarity_score'] * 100)
                            matched_count = len(rec['matched_ingredients'])
                            total_count = matched_count + len(rec['missing_ingredients'])
                            
                            st.write(f"**Direkomendasikan karena {matched_count} dari {total_count} bahan tersedia dengan similarity score {score_percent}%.**")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Category:** {rec['category']}")
                            with col2:
                                st.write(f"❤️ **Loves:** {rec['loves']}")
                                
                            with st.expander("Lihat Detail Resep"):
                                st.write("**Bahan yang cocok:**")
                                if rec['matched_ingredients']:
                                    st.write(", ".join(rec['matched_ingredients']))
                                else:
                                    st.write("-")
                                    
                                st.write("**Bahan yang kurang:**")
                                if rec['missing_ingredients']:
                                    st.write(", ".join(rec['missing_ingredients']))
                                else:
                                    st.write("-")
                                
                                st.markdown("---")
                                st.write("**Full Ingredients:**")
                                st.write(rec['ingredients'])
                                
                                st.markdown("---")
                                st.write("**Cooking Steps:**")
                                st.write(rec['steps'])
                                
                                st.markdown("---")
                                st.write(f"[Sumber Resep]({rec['url']})")
                            st.divider()
                else:
                    st.error(f"Terjadi kesalahan pada server: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Gagal terhubung ke server backend. Pastikan backend sudah berjalan (uvicorn backend.main:app --reload).")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
