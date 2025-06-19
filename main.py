# main.py
import streamlit as st
import pandas as pd
import time
from pathlib import Path
from data_loader import load_all_data
from scheduler import jadwalkan_ai as jadwalkan
import base64

# === KONFIGURASI HALAMAN ===
st.set_page_config(
    page_title="AI Penjadwalan Kuliah",
    layout="wide",
    page_icon="📅",
    initial_sidebar_state="expanded"
)

# === SETUP FOLDER ===
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

JADWAL_PATH = OUTPUT_DIR / "jadwal_kuliah.csv"

# === SIDEBAR NAVIGATION ===
st.sidebar.title("📅 Menu Navigasi")
menu = st.sidebar.selectbox(
    "Pilih Menu:",
    ["🏠 Beranda", "📤 Upload Data", "✏️ Edit Data", "🗓 Generate Jadwal", "📋 Hasil Jadwal"]
)

# === FUNGSI HELPER ===
def create_template_download():
    # Buat template dalam bentuk zip
    import zipfile
    from io import BytesIO
    
    # Buat DataFrame untuk masing-masing template
    template_matkul = pd.DataFrame(columns=["kode_matkul", "nama_matkul", "sks", "kelas", "dosen"])
    template_dosen = pd.DataFrame(columns=["kode_dosen", "nama_dosen", "preferensi_hari", "preferensi_sesi"])
    template_kelas = pd.DataFrame(columns=["kode_kelas", "jumlah_mahasiswa"])
    template_ruangan = pd.DataFrame(columns=["kode_ruang", "kapasitas", "tersedia_hari", "tersedia_sesi"])
    
    # Tambahkan contoh data
    template_matkul.loc[0] = ["MK001", "Kalkulus", 3, "A1", "D001"]
    template_dosen.loc[0] = ["D001", "Dr. Ahmad", "Senin,Selasa", "1,2"]
    template_kelas.loc[0] = ["A1", 40]
    template_ruangan.loc[0] = ["R101", 50, "Senin,Selasa,Rabu", "1,2,3"]
    
    # Buat file zip di memori
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr('matkul_template.csv', template_matkul.to_csv(index=False))
        zip_file.writestr('dosen_template.csv', template_dosen.to_csv(index=False))
        zip_file.writestr('kelas_template.csv', template_kelas.to_csv(index=False))
        zip_file.writestr('ruangan_template.csv', template_ruangan.to_csv(index=False))
    
    return zip_buffer.getvalue()

def save_dataframe_to_csv(df, filename):
    file_path = DATA_DIR / filename
    df.to_csv(file_path, index=False)
    return file_path

def file_exists(file_name):
    return (DATA_DIR / file_name).exists()

def create_dummy_data():
    # Buat data dummy untuk demonstrasi
    matkul = pd.DataFrame({
        "kode_matkul": ["MK001", "MK002", "MK003"],
        "nama_matkul": ["Kalkulus", "Fisika Dasar", "Pemrograman"],
        "sks": [3, 3, 4],
        "kelas": ["A1", "A2", "B1"],
        "dosen": ["D001", "D002", "D003"]
    })
    
    dosen = pd.DataFrame({
        "kode_dosen": ["D001", "D002", "D003"],
        "nama_dosen": ["Dr. Ahmad", "Prof. Budi", "Dr. Citra"],
        "preferensi_hari": ["Senin,Selasa", "Rabu,Kamis", "Jumat"],
        "preferensi_sesi": ["1,2", "3,4", "1,2,3"]
    })
    
    kelas = pd.DataFrame({
        "kode_kelas": ["A1", "A2", "B1"],
        "jumlah_mahasiswa": [40, 35, 30]
    })
    
    ruangan = pd.DataFrame({
        "kode_ruang": ["R101", "R102", "R201"],
        "kapasitas": [50, 45, 40],
        "tersedia_hari": ["Senin,Selasa,Rabu", "Kamis,Jumat", "Senin-Selasa-Rabu-Kamis-Jumat"],
        "tersedia_sesi": ["1,2,3", "1,2,3,4", "1,2,3,4,5"]
    })
    
    matkul.to_csv(DATA_DIR / "matkul.csv", index=False)
    dosen.to_csv(DATA_DIR / "dosen.csv", index=False)
    kelas.to_csv(DATA_DIR / "kelas.csv", index=False)
    ruangan.to_csv(DATA_DIR / "ruangan.csv", index=False)
    st.success("✅ Data demo berhasil dibuat!")

# Inisialisasi data
if "initialized" not in st.session_state:
    # Hanya dijalankan sekali saat aplikasi pertama kali dibuka
    st.session_state.initialized = True
    st.session_state.use_dummy_data = False

# === HALAMAN BERANDA ===
if menu == "🏠 Beranda":
    st.title("📅 Sistem Penjadwalan Kuliah Otomatis Berbasis AI")
    
    # Hapus class success-box
    st.info("""
    **Selamat datang di Sistem Penjadwalan Kuliah Otomatis!**\n
    Sistem ini menggunakan algoritma AI untuk menghasilkan jadwal kuliah optimal berdasarkan preferensi dosen, ketersediaan ruangan, dan kebutuhan mata kuliah.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📋 Fitur Utama")
        st.markdown("""
        - Upload data via CSV atau input manual
        - Edit data secara interaktif
        - Generate jadwal otomatis berbasis AI
        - Ekspor jadwal ke format CSV
        - Visualisasi jadwal kuliah
        """)
    
    with col2:
        st.subheader("🚀 Cara Menggunakan")
        st.markdown("""
        1. Upload data melalui menu **Upload Data**
        2. Edit data di menu **Edit Data**
        3. Generate jadwal di menu **Generate Jadwal**
        4. Lihat hasil di menu **Hasil Jadwal**
        """)
    
    with col3:
        st.subheader("📊 Keunggulan")
        st.markdown("""
        - Optimasi penggunaan ruangan
        - Penghindaran konflik jadwal
        - Memenuhi preferensi dosen
        - Tampilan visual yang informatif
        - Proses otomatis dan efisien
        """)
    
    st.markdown("---")
    st.subheader("⚡ Mulai Cepat")
    
    if st.button("🔄 Gunakan Data Demo", use_container_width=True):
        create_dummy_data()
        st.session_state.use_dummy_data = True
        st.success("Data demo berhasil dimuat! Silakan lanjut ke menu Generate Jadwal")
        time.sleep(1)
        st.experimental_set_query_params(menu="🤖 Generate Jadwal")
        st.rerun()

# === MENU 1: UPLOAD DATA ===
elif menu == "📤 Upload Data":
    st.title("📤 Upload Data Penjadwalan")
    
    tab1, tab2 = st.tabs(["📁 Upload File CSV", "➕ Input Manual"])
    
    with tab1:
        st.header("📁 Upload File CSV")
        st.markdown("Silakan upload file CSV untuk masing-masing data:")
        
        template_zip = create_template_download()
        st.download_button(
            label="📥 Download Template CSV",
            data=template_zip,
            file_name="template_jadwal.zip",
            mime="application/zip"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📘 Data Mata Kuliah")
            matkul_file = st.file_uploader("Upload matkul.csv", type=['csv'], key="matkul_upload")
            if matkul_file:
                matkul_df = pd.read_csv(matkul_file)
                matkul_df.to_csv(DATA_DIR / "matkul.csv", index=False)
                st.success("File matkul.csv berhasil diunggah!")
                st.dataframe(matkul_df.head())
            
            st.subheader("👥 Data Kelas Mahasiswa")
            kelas_file = st.file_uploader("Upload kelas.csv", type=['csv'], key="kelas_upload")
            if kelas_file:
                kelas_df = pd.read_csv(kelas_file)
                kelas_df.to_csv(DATA_DIR / "kelas.csv", index=False)
                st.success("File kelas.csv berhasil diunggah!")
                st.dataframe(kelas_df.head())

        with col2:
            st.subheader("👨‍🏫 Data Dosen Pengampu")
            dosen_file = st.file_uploader("Upload dosen.csv", type=['csv'], key="dosen_upload")
            if dosen_file:
                dosen_df = pd.read_csv(dosen_file)
                dosen_df.to_csv(DATA_DIR / "dosen.csv", index=False)
                st.success("File dosen.csv berhasil diunggah!")
                st.dataframe(dosen_df.head())
            
            st.subheader("🏫 Data Ruangan")
            ruangan_file = st.file_uploader("Upload ruangan.csv", type=['csv'], key="ruangan_upload")
            if ruangan_file:
                ruangan_df = pd.read_csv(ruangan_file)
                ruangan_df.to_csv(DATA_DIR / "ruangan.csv", index=False)
                st.success("File ruangan.csv berhasil diunggah!")
                st.dataframe(ruangan_df.head())
    
    with tab2:
        st.header("➕ Input Manual")
        st.markdown("Isi data secara manual menggunakan form di bawah ini:")
        
        tab_mk, tab_dosen, tab_kelas, tab_ruang = st.tabs(["Mata Kuliah", "Dosen", "Kelas", "Ruangan"])
        
        with tab_mk:
            with st.form("form_matkul_manual"):
                st.subheader("📝 Tambah Mata Kuliah")
                kode = st.text_input("Kode Mata Kuliah*", placeholder="MK001")
                nama = st.text_input("Nama Mata Kuliah*", placeholder="Kalkulus")
                sks = st.number_input("SKS*", min_value=1, max_value=6, value=3)
                kelas = st.text_input("Kelas*", placeholder="A1")
                dosen = st.text_input("Kode Dosen Pengampu*", placeholder="D001")
                
                submitted = st.form_submit_button("💾 Simpan Mata Kuliah")
                if submitted:
                    if not all([kode, nama, kelas, dosen]):
                        st.error("Harap isi semua field yang wajib diisi (*)")
                    else:
                        new_row = pd.DataFrame([[kode, nama, sks, kelas, dosen]], 
                                             columns=["kode_matkul", "nama_matkul", "sks", "kelas", "dosen"])
                        
                        if file_exists("matkul.csv"):
                            df = pd.read_csv(DATA_DIR / "matkul.csv")
                            df = pd.concat([df, new_row], ignore_index=True)
                        else:
                            df = new_row
                            
                        df.to_csv(DATA_DIR / "matkul.csv", index=False)
                        st.success("✅ Mata kuliah berhasil ditambahkan!")
        
        with tab_dosen:
            with st.form("form_dosen_manual"):
                st.subheader("👨‍🏫 Tambah Dosen")
                kode = st.text_input("Kode Dosen*", placeholder="D001")
                nama = st.text_input("Nama Dosen*", placeholder="Dr. Ahmad")
                hari = st.multiselect("Preferensi Hari", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"], default=["Senin", "Selasa"])
                sesi = st.multiselect("Preferensi Sesi", [1, 2, 3, 4, 5], default=[1, 2])
                
                submitted = st.form_submit_button("💾 Simpan Dosen")
                if submitted:
                    if not kode or not nama:
                        st.error("Harap isi semua field yang wajib diisi (*)")
                    else:
                        new_row = pd.DataFrame([[kode, nama, ",".join(hari), ",".join(map(str, sesi))]], 
                                             columns=["kode_dosen", "nama_dosen", "preferensi_hari", "preferensi_sesi"])
                        
                        if file_exists("dosen.csv"):
                            df = pd.read_csv(DATA_DIR / "dosen.csv")
                            df = pd.concat([df, new_row], ignore_index=True)
                        else:
                            df = new_row
                            
                        df.to_csv(DATA_DIR / "dosen.csv", index=False)
                        st.success("✅ Dosen berhasil ditambahkan!")
        
        with tab_kelas:
            with st.form("form_kelas_manual"):
                st.subheader("👥 Tambah Kelas")
                kode = st.text_input("Kode Kelas*", placeholder="A1")
                jumlah = st.number_input("Jumlah Mahasiswa*", min_value=1, value=40)
                
                submitted = st.form_submit_button("💾 Simpan Kelas")
                if submitted:
                    if not kode:
                        st.error("Harap isi semua field yang wajib diisi (*)")
                    else:
                        new_row = pd.DataFrame([[kode, jumlah]], 
                                             columns=["kode_kelas", "jumlah_mahasiswa"])
                        
                        if file_exists("kelas.csv"):
                            df = pd.read_csv(DATA_DIR / "kelas.csv")
                            df = pd.concat([df, new_row], ignore_index=True)
                        else:
                            df = new_row
                            
                        df.to_csv(DATA_DIR / "kelas.csv", index=False)
                        st.success("✅ Kelas berhasil ditambahkan!")
        
        with tab_ruang:
            with st.form("form_ruangan_manual"):
                st.subheader("🏫 Tambah Ruangan")
                kode = st.text_input("Kode Ruangan*", placeholder="R101")
                kapasitas = st.number_input("Kapasitas*", min_value=1, value=50)
                hari = st.multiselect("Hari Tersedia", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"], 
                                    default=["Senin", "Selasa", "Rabu", "Kamis", "Jumat"])
                sesi = st.multiselect("Sesi Tersedia", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5])
                
                submitted = st.form_submit_button("💾 Simpan Ruangan")
                if submitted:
                    if not kode:
                        st.error("Harap isi semua field yang wajib diisi (*)")
                    else:
                        new_row = pd.DataFrame([[kode, kapasitas, ",".join(hari), ",".join(map(str, sesi))]], 
                                             columns=["kode_ruang", "kapasitas", "tersedia_hari", "tersedia_sesi"])
                        
                        if file_exists("ruangan.csv"):
                            df = pd.read_csv(DATA_DIR / "ruangan.csv")
                            df = pd.concat([df, new_row], ignore_index=True)
                        else:
                            df = new_row
                            
                        df.to_csv(DATA_DIR / "ruangan.csv", index=False)
                        st.success("✅ Ruangan berhasil ditambahkan!")

# === MENU 2: EDIT DATA ===
elif menu == "✏️ Edit Data":
    st.title("✏️ Edit Data Penjadwalan")
    
    # Cek ketersediaan data
    files_exist = {
        "Mata Kuliah": file_exists("matkul.csv"),
        "Dosen": file_exists("dosen.csv"),
        "Kelas": file_exists("kelas.csv"),
        "Ruangan": file_exists("ruangan.csv")
    }
    
    # Tampilkan status data
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mata Kuliah", "✅" if files_exist["Mata Kuliah"] else "❌")
    with col2:
        st.metric("Dosen", "✅" if files_exist["Dosen"] else "❌")
    with col3:
        st.metric("Kelas", "✅" if files_exist["Kelas"] else "❌")
    with col4:
        st.metric("Ruangan", "✅" if files_exist["Ruangan"] else "❌")
    
    if not any(files_exist.values()):
        st.warning("⚠️ Belum ada data yang diupload. Silakan upload file CSV terlebih dahulu di menu **Upload Data**.")
        st.info("💡 Atau Anda bisa menambahkan data manual menggunakan form di menu Upload Data.")
        st.stop()
    
    tab_edit = st.tabs(["📘 Mata Kuliah", "👨‍🏫 Dosen", "👥 Kelas", "🏫 Ruangan"])
    
    # === TAB MATA KULIAH ===
    with tab_edit[0]:
        if file_exists("matkul.csv"):
            df = pd.read_csv(DATA_DIR / "matkul.csv")
            st.subheader("📘 Data Mata Kuliah")
            
            edited_df = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "kode_matkul": st.column_config.TextColumn("Kode*", required=True),
                    "nama_matkul": st.column_config.TextColumn("Nama*", required=True),
                    "sks": st.column_config.NumberColumn("SKS*", min_value=1, max_value=6, step=1, required=True),
                    "kelas": st.column_config.TextColumn("Kelas*", required=True),
                    "dosen": st.column_config.TextColumn("Dosen*", required=True)
                }
            )
            
            if st.button("💾 Simpan Perubahan Mata Kuliah", use_container_width=True):
                edited_df.to_csv(DATA_DIR / "matkul.csv", index=False)
                st.success("✅ Perubahan data mata kuliah berhasil disimpan!")
        else:
            st.warning("Data mata kuliah belum tersedia")
    
    # === TAB DOSEN ===
    with tab_edit[1]:
        if file_exists("dosen.csv"):
            df = pd.read_csv(DATA_DIR / "dosen.csv")
            df["preferensi_sesi"] = df["preferensi_sesi"].astype(str)
            st.subheader("👨‍🏫 Data Dosen")
            
            edited_df = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "kode_dosen": st.column_config.TextColumn("Kode*", required=True),
                    "nama_dosen": st.column_config.TextColumn("Nama*", required=True),
                    "preferensi_hari": st.column_config.TextColumn("Hari Preferensi"),
                    "preferensi_sesi": st.column_config.TextColumn("Sesi Preferensi")
                }
            )
            
            if st.button("💾 Simpan Perubahan Dosen", use_container_width=True):
                edited_df.to_csv(DATA_DIR / "dosen.csv", index=False)
                st.success("✅ Perubahan data dosen berhasil disimpan!")
        else:
            st.warning("Data dosen belum tersedia")
    
    # === TAB KELAS ===
    with tab_edit[2]:
        if file_exists("kelas.csv"):
            df = pd.read_csv(DATA_DIR / "kelas.csv")
            st.subheader("👥 Data Kelas")
            
            edited_df = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "kode_kelas": st.column_config.TextColumn("Kode*", required=True),
                    "jumlah_mahasiswa": st.column_config.NumberColumn("Jumlah*", min_value=1, step=1, required=True)
                }
            )
            
            if st.button("💾 Simpan Perubahan Kelas", use_container_width=True):
                edited_df.to_csv(DATA_DIR / "kelas.csv", index=False)
                st.success("✅ Perubahan data kelas berhasil disimpan!")
        else:
            st.warning("Data kelas belum tersedia")
    
    # === TAB RUANGAN ===
    with tab_edit[3]:
        if file_exists("ruangan.csv"):
            df = pd.read_csv(DATA_DIR / "ruangan.csv")
            df["tersedia_sesi"] = df["tersedia_sesi"].astype(str)
            st.subheader("🏫 Data Ruangan")
            
            edited_df = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "kode_ruang": st.column_config.TextColumn("Kode*", required=True),
                    "kapasitas": st.column_config.NumberColumn("Kapasitas*", min_value=1, step=1, required=True),
                    "tersedia_hari": st.column_config.TextColumn("Hari Tersedia"),
                    "tersedia_sesi": st.column_config.TextColumn("Sesi Tersedia")
                }
            )
            
            if st.button("💾 Simpan Perubahan Ruangan", use_container_width=True):
                edited_df.to_csv(DATA_DIR / "ruangan.csv", index=False)
                st.success("✅ Perubahan data ruangan berhasil disimpan!")
        else:
            st.warning("Data ruangan belum tersedia")

# === MENU 3: GENERATE JADWAL ===
elif menu == "🗓 Generate Jadwal":
    st.title("🗓 Generate Jadwal Otomatis")
    
    # Cek ketersediaan data
    files_exist = {
        "matkul": file_exists("matkul.csv"),
        "dosen": file_exists("dosen.csv"),
        "kelas": file_exists("kelas.csv"),
        "ruangan": file_exists("ruangan.csv")
    }
    
    missing_files = [name for name, exists in files_exist.items() if not exists]
    
    if missing_files:
        st.error(f"❌ Data tidak lengkap! File yang hilang: {', '.join(missing_files)}")
        st.info("💡 Silakan upload semua file CSV terlebih dahulu di menu **Upload Data** atau tambahkan data di menu **Edit Data**.")
        st.stop()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ Konfigurasi Penjadwalan")
        
        # Input parameter algoritma
        population_size = st.slider("Ukuran Populasi", 50, 500, 100, 50)
        generations = st.slider("Jumlah Generasi", 100, 1000, 300, 50)
        mutation_rate = st.slider("Tingkat Mutasi", 0.01, 0.5, 0.1, 0.01)
        
        st.info("""
        **Penjelasan Parameter:**
        - **Ukuran Populasi**: Jumlah solusi yang dievaluasi setiap generasi
        - **Jumlah Generasi**: Iterasi algoritma genetika
        - **Tingkat Mutasi**: Probabilitas terjadinya mutasi pada kromosom
        """)
    
    with col2:
        st.subheader("🚀 Proses Penjadwalan")
        
        if st.button("🔄 Mulai Generate Jadwal", use_container_width=True, type="primary"):
            try:
                # Load data
                with st.spinner("📊 Memuat data..."):
                    matkul, dosen, kelas, ruangan = load_all_data()
                
                # Validasi data
                if matkul.empty:
                    st.error("❌ Data mata kuliah kosong!")
                    st.stop()
                
                # Proses penjadwalan
                with st.spinner("🧠 Menghitung jadwal optimal..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simulasi progress
                    for i in range(10):
                        progress = (i + 1) * 10
                        progress_bar.progress(progress)
                        status_text.text(f"Proses penjadwalan... {progress}%")
                        time.sleep(0.2)
                    
                    # Panggil fungsi penjadwalan
                    df_jadwal = jadwalkan(
                        matkul, 
                        dosen, 
                        kelas, 
                        ruangan,
                        population_size=population_size,
                        generations=generations,
                        mutation_rate=mutation_rate
                    )
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Jadwal berhasil dibuat!")
                    time.sleep(1)
                
                # Simpan hasil
                st.session_state["jadwal"] = df_jadwal
                df_jadwal.to_csv(JADWAL_PATH, index=False)
                
                st.success(f"✅ Jadwal berhasil dibuat dengan {len(df_jadwal)} mata kuliah terjadwal!")
                st.balloons()
                
                # Tampilkan preview
                st.subheader("📋 Preview Jadwal")
                st.dataframe(df_jadwal.head())
                
                # Tombol untuk lihat hasil lengkap
                if st.button("Lihat Jadwal Lengkap", use_container_width=True):
                    st.experimental_set_query_params(menu="📋 Hasil Jadwal")
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error saat menjadwalkan: {str(e)}")
                with st.expander("🔍 Detail Error"):
                    st.exception(e)

# === MENU 4: HASIL JADWAL ===
elif menu == "📋 Hasil Jadwal":
    st.title("📋 Hasil Jadwal Kuliah")
    
    if "jadwal" in st.session_state:
        df_jadwal = st.session_state["jadwal"]
    elif JADWAL_PATH.exists():
        try:
            df_jadwal = pd.read_csv(JADWAL_PATH)
            st.session_state["jadwal"] = df_jadwal
        except:
            st.error("❌ Gagal memuat file jadwal. Format mungkin tidak sesuai.")
            st.stop()
    else:
        st.warning("Belum ada jadwal yang dibuat. Silakan buat jadwal terlebih dahulu di menu Generate Jadwal.")
        st.stop()
    
    # Statistik jadwal
    st.subheader("📊 Statistik Jadwal")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Mata Kuliah", len(df_jadwal))
    with col2:
        st.metric("Jumlah Dosen Terlibat", df_jadwal['dosen'].nunique())
    with col3:
        st.metric("Jumlah Ruangan Digunakan", df_jadwal['ruangan'].nunique())
    with col4:
        st.metric("Jumlah Kelas Terjadwal", df_jadwal['kelas'].nunique())
    
    # Tampilkan jadwal
    st.subheader("📅 Jadwal Kuliah")
    
    # Filter data
    col1, col2 = st.columns(2)
    with col1:
        hari_filter = st.multiselect("Filter Hari", options=df_jadwal['hari'].unique(), default=df_jadwal['hari'].unique())
    with col2:
        dosen_filter = st.multiselect("Filter Dosen", options=df_jadwal['dosen'].unique(), default=df_jadwal['dosen'].unique())
    
    filtered_df = df_jadwal[
        (df_jadwal['hari'].isin(hari_filter)) & 
        (df_jadwal['dosen'].isin(dosen_filter))
    ]
    
    st.dataframe(filtered_df, use_container_width=True, height=500)
    
    # Visualisasi jadwal
    st.subheader("📊 Visualisasi Jadwal")
    tab1, tab2 = st.tabs(["Per Hari", "Per Ruangan"])
    
    with tab1:
        hari_pilihan = st.selectbox("Pilih Hari", options=df_jadwal['hari'].unique())
        hari_df = df_jadwal[df_jadwal['hari'] == hari_pilihan].sort_values('sesi')
        
        if not hari_df.empty:
            st.bar_chart(
                hari_df.groupby('sesi').size()
            )
            
            st.subheader(f"Detail Jadwal Hari {hari_pilihan}")
            st.dataframe(hari_df)
        else:
            st.info(f"Tidak ada jadwal pada hari {hari_pilihan}")
    
    with tab2:
        ruangan_pilihan = st.selectbox("Pilih Ruangan", options=df_jadwal['ruangan'].unique())
        ruangan_df = df_jadwal[df_jadwal['ruangan'] == ruangan_pilihan].sort_values(['hari', 'sesi'])
        
        if not ruangan_df.empty:
            # Buat pivot table untuk heatmap
            pivot_df = ruangan_df.pivot_table(
                index='sesi', 
                columns='hari', 
                values='nama_matkul', 
                aggfunc=lambda x: ', '.join(x)
            ).fillna('')
            
            # Tampilkan heatmap tanpa styling
            st.dataframe(pivot_df)
        else:
            st.info(f"Tidak ada jadwal di ruangan {ruangan_pilihan}")
    
    # Ekspor jadwal
    st.subheader("📤 Ekspor Jadwal")
    csv = df_jadwal.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Jadwal (CSV)",
        data=csv,
        file_name="jadwal_kuliah.csv",
        mime="text/csv",
        use_container_width=True
    )

# === SIDEBAR FOOTER ===
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Status Data")

# Cek ketersediaan file
files_status = {
    "Mata Kuliah": file_exists("matkul.csv"),
    "Dosen": file_exists("dosen.csv"),
    "Kelas": file_exists("kelas.csv"),
    "Ruangan": file_exists("ruangan.csv")
}

for name, exists in files_status.items():
    if exists:
        st.sidebar.success(f"✅ {name}")
    else:
        st.sidebar.error(f"❌ {name}")

# Reset aplikasi
if st.sidebar.button("🔄 Reset Aplikasi", use_container_width=True):
    for file in ["matkul.csv", "dosen.csv", "kelas.csv", "ruangan.csv"]:
        path = DATA_DIR / file
        if path.exists():
            path.unlink()
    if "jadwal" in st.session_state:
        del st.session_state["jadwal"]
    st.sidebar.success("Aplikasi berhasil direset!")
    time.sleep(1)
    st.experimental_set_query_params(menu="🏠 Beranda")
    st.rerun()