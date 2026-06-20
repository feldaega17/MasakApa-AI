import streamlit as st
import sys
import os

# Ensure backend can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.recommender import recommender_engine

st.set_page_config(page_title="MasakApa AI", layout="centered", page_icon="🍳")

st.title("MasakApa AI")
st.write("Temukan ide masakan berdasarkan bahan yang tersedia.")

# --- Filters ---
col1, col2 = st.columns(2)
with col1:
    category_filter = st.selectbox(
        "Kategori Resep",
        ["Semua Kategori", "Ayam", "Sapi", "Sayur", "Seafood", "Kue", "Minuman", "Nasi", "Mie"]
    )
with col2:
    sort_filter = st.selectbox(
        "Urutkan Berdasarkan",
        ["Paling Relevan", "Paling Praktis (Sedikit Langkah)"]
    )

sort_val = "practicality" if "Praktis" in sort_filter else "relevance"

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
                # Direct inference
                recommendations = recommender_engine.get_recommendations(
                    user_ingredients=ingredients_input,
                    category=category_filter,
                    sort_by=sort_val
                )
                
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
                        
                        col1_1, col2_1 = st.columns(2)
                        with col1_1:
                            st.write(f"**Category:** {rec['category']}")
                        with col2_1:
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
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
