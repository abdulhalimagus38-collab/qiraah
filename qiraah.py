import streamlit as st
import google.generativeai as generative_ai

# ==========================================
# CONFIGURATION
# ==========================================
st.set_page_config(page_title="Pusat Pembelajaran Maharah Qira'ah", page_icon="👨‍🏫", layout="wide")

# Kustomisasi CSS Warna Putih & Biru Akademik
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e293b; }
    .stButton>button { background-color: #2563eb; color: white; border-radius: 8px; border: none; }
    .stButton>button:hover { background-color: #1d4ed8; color: white; }
    .css-11756fd { background-color: #f8fafc; border-right: 1px solid #e2e8f0; }
    div[data-testid="stChatMessage"] { border-radius: 12px; padding: 15px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR: SETTING KEY, GURU, & MATERI
# ==========================================
with st.sidebar:
    st.subheader("🔑 Pengaturan API")
    api_key = st.text_input("Gemini API Key:", type="password", placeholder="Masukkan key Anda...")
    
    st.markdown("---")
    st.subheader("🧑‍🏫 Pilih Guru Pembimbing")
    pilihan_guru = st.radio(
        "Pilih guru yang kamu inginkan:",
        ("Ustaz Jamal", "Ustazah Hana")
    )
    
    st.markdown("---")
    st.subheader("📚 Pilihan Materi")
    pilihan_materi = st.radio(
        "Pilih tema materi yang ingin dipelajari:",
        (
            "1. فِي السُّوقِ (Di Pasar)",
            "2. هِوَايَتِي (Hobiku)",
            "3. يَوْمٌ فِي الْمَدْرَسَةِ (Sehari di Sekolah)",
            "4. الْمِهْنَةُ (Profesi)"
        )
    )

# Tentukan ikon dan detail sapaan berdasarkan guru yang dipilih
if pilihan_guru == "Ustaz Jamal":
    nama_guru = "Ustaz Jamal"
    ikon_guru = "👨‍🏫"
    gender_self = "Anda adalah 'Ustaz Jamal', seorang tutor AI laki-laki yang ramah, sabar, dan suportif."
    sapaan_awal = "أَهْلًا وَسَهْلًا بِكَ! أَنَا أُسْتَاذُ جَمَال، صَدِيقُكَ لِتَدْرِيبِ مَهَارَةِ الْقِرَاءَةِ بِاللُّغَةِ الْعَرَبِيَّةِ.\n*(Selamat datang! Saya Ustaz Jamal, teman kamu untuk melatih keterampilan membaca bahasa Arab.)*"
else:
    nama_guru = "Ustazah Hana"
    ikon_guru = "👩‍🏫"
    gender_self = "Anda adalah 'Ustazah Hana', seorang tutor AI perempuan yang santun, keibuan, lembut, dan detail dalam mengoreksi."
    sapaan_awal = "أَهْلًا وَسَهْلًا بِكِ! أَنَا أُسْتَاذَة هَنَا، مُرَبِّيَتُكِ لِتَدْرِيبِ مَهَارَةِ الْقِرَاءَةِ بِاللُّغَةِ الْعَرَبِيَّةِ.\n*(Selamat datang! Saya Ustazah Hana, pembimbingmu untuk melatih keterampilan membaca bahasa Arab.)*"

# ==========================================
# DYNAMIC SYSTEM PROMPT
# ==========================================
SYSTEM_PROMPT = f"""
Konteks Sistem: {gender_self} Anda berperan sebagai pembimbing Maharah Qira'ah (keterampilan membaca) dan pemahaman kosakata (Mufrodat) bahasa Arab khusus untuk siswa MTs Kelas 9 di Indonesia.

Tujuan Utama:
Melatih siswa membaca teks Arab berharakat dengan akurat (huruf, harakat, dan kata yang tepat), menguji pemahaman isi teks, serta menjelaskan kosakata (mufrodat) dari tema aktif yang dipilih siswa.

Materi Aktif Saat Ini yang Wajib Difokuskan: {pilihan_materi}

Aturan Khusus Chat:
1. Sapa siswa sesuai dengan karakter Anda ({nama_guru}). Jika siswa bertanya tentang kosakata/mufrodat, berikan penjelasan yang santun, sebutkan artinya, cara baca, dan berikan 1 contoh kalimat pendek berharakat lengkap beserta terjemahannya.
2. Semua teks Arab (judul, bacaan, instruksi, pertanyaan) WAJIB berharakat lengkap.
3. Setiap blok teks Arab WAJIB diikuti terjemahan Bahasa Indonesia di baris bawahnya dalam tanda kurung dan miring. Contoh: النَّصُّ: فِي الْمَدْرَسَةِ (Teks: Di Sekolah).
4. Jika mengoreksi ketikan membaca siswa, gunakan format pembatas [Tips {nama_guru}] lalu jelaskan kesalahannya dalam Bahasa Indonesia secara singkat dan santun.
Pahami instruksi ini, jawab pesan siswa dengan ramah sesuai aturan ini.
"""

# ==========================================
# INITIALIZATION STATE
# ==========================================
if "current_guru" not in st.session_state or "current_materi" not in st.session_state:
    st.session_state.current_guru = nama_guru
    st.session_state.current_materi = pilihan_materi
    st.session_state.messages = []

if st.session_state.current_guru != nama_guru or st.session_state.current_materi != pilihan_materi:
    st.session_state.current_guru = nama_guru
    st.session_state.current_materi = pilihan_materi
    st.session_state.messages = []

# Jika chat kosong, isi dengan sapaan awal
if len(st.session_state.messages) == 0:
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"{sapaan_awal}\n\nKamu telah memilih materi **{pilihan_materi}**. Mari kita mulai belajarnya! Silakan sapa {nama_guru} untuk memulai."
    })

# ==========================================
# MAIN INTERFACE: CHATBOT
# ==========================================
st.title(f"{ikon_guru} {nama_guru} - Pembimbing Qira'ah & Mufrodat")
st.info(f"📋 **Materi Aktif:** {pilihan_materi}")

# Tampilkan riwayat obrolan
for msg in st.session_state.messages:
    role_icon = ikon_guru if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=role_icon):
        st.markdown(msg["content"])

# Input Chat Utama
if user_input := st.chat_input(f"Ketik balasan Anda atau jawab pertanyaan {nama_guru} di sini..."):
    # Tampilkan & simpan input user
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    # Buat history SEBELUM user_input yang baru dimasukkan ke session_state agar urutan selang-seling API terjaga
    formatted_history = []
    # Lewati indeks ke-0 karena itu sapaan lokal buatan Streamlit
    for m in st.session_state.messages[1:]:
        formatted_history.append({
            "role": "user" if m["role"] == "user" else "model",
            "parts": [m["content"]]
        })
        
    # Sekarang baru simpan input user ke state utama
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Respon Assistant
    with st.chat_message("assistant", avatar=ikon_guru):
        if api_key:
            try:
                with st.spinner(f"{nama_guru} sedang membaca jawabanmu..."):
                    # Konfigurasi kunci API aktif
                    generative_ai.configure(api_key=api_key)
                    
                    # 🌟 PERBAIKAN: Menggunakan gemini-2.5-flash sebagai model default yang aktif & stabil
                    model = generative_ai.GenerativeModel(
                        model_name="gemini-2.5-flash",
                        system_instruction=SYSTEM_PROMPT
                    )
                    
                    # Jalankan chat dengan history yang telah disterilkan
                    chat = model.start_chat(history=formatted_history)
                    response = chat.send_message(user_input)
                    res_text = response.text
                    
            except Exception as e:
                res_text = f"Terjadi kesalahan koneksi API: {str(e)}\n\n*Tips: Pastikan API Key dari Google AI Studio sudah benar, aktif, dan library 'google-generativeai' Anda sudah diperbarui.*"
        else:
            res_text = f"بَارَكَ اللّٰهُ فِيكَ! {nama_guru} menerima pesanmu: *'{user_input}'*.\n\n*(Catatan: Mode Offline aktif. Silakan isi API Key di bilah samping kiri agar {nama_guru} dapat mengoreksi harakat membaca dan memberikan pertanyaan interaktif!)*"
            
        st.markdown(res_text)
        st.session_state.messages.append({"role": "assistant", "content": res_text})
        st.rerun()