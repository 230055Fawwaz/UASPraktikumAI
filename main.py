# main.py
import streamlit as st
import pandas as pd
from pathlib import Path
from data_loader import load_all_data
from scheduler import jadwalkan_ai as jadwalkan

st.set_page_config(page_title="AI Penjadwalan Kuliah", layout="wide")

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
    ["📤 Upload Data CSV", "✏️ Edit Data", "🔄 Jadwal & Reset"]
)

st.title("📅 Sistem Penjadwalan Kuliah Otomatis Berbasis AI")

# === FUNGSI HELPER ===
def upload_and_preview(label, key):
    file = st.file_uploader(label, type=['csv'], key=key)
    if file:
        df = pd.read_csv(file)
        df.to_csv(DATA_DIR / f"{key}.csv", index=False)
        st.success(f"File {key}.csv berhasil diunggah!")
        st.dataframe(df)
        return df
    return None

def save_dataframe_to_csv(df, filename):
    """Fungsi untuk menyimpan DataFrame ke CSV"""
    file_path = DATA_DIR / filename
    df.to_csv(file_path, index=False)
    return file_path

# === MENU 1: UPLOAD DATA CSV ===
if menu == "📤 Upload Data CSV":
    st.header("📤 Upload File CSV")
    st.markdown("Silakan upload file CSV untuk masing-masing data:")
    
    col1, col2 = st.columns(2)
    with col1:
        df_matkul = upload_and_preview("📘 Data Mata Kuliah", "matkul")
        df_kelas = upload_and_preview("👥 Data Kelas Mahasiswa", "kelas")

    with col2:
        df_dosen = upload_and_preview("👨‍🏫 Data Dosen Pengampu", "dosen")
        df_ruangan = upload_and_preview("🏫 Data Ruangan", "ruangan")
    
    st.info("💡 **Format CSV yang diharapkan:**")
    st.markdown("""
    - **Dosen**: `kode_dosen, nama_dosen, preferensi_hari, preferensi_sesi`
    - **Kelas**: `kode_kelas, jumlah_mahasiswa`
    - **Mata Kuliah**: `kode_matkul, nama_matkul, sks, kelas, dosen`
    - **Ruangan**: `kode_ruang, kapasitas, tersedia_hari, tersedia_sesi`
    """)

# === MENU 2: EDIT DATA ===
elif menu == "✏️ Edit Data":
    st.header("✏️ Edit & Kelola Data")
    
    # Cek apakah ada file yang sudah diupload
    files_exist = {
        "matkul": (DATA_DIR / "matkul.csv").exists(),
        "dosen": (DATA_DIR / "dosen.csv").exists(),
        "kelas": (DATA_DIR / "kelas.csv").exists(),
        "ruangan": (DATA_DIR / "ruangan.csv").exists()
    }
    
    if not any(files_exist.values()):
        st.warning("⚠️ Belum ada data yang diupload. Silakan upload file CSV terlebih dahulu di menu **Upload Data CSV**.")
        st.info("💡 Atau Anda bisa menambahkan data manual menggunakan form di bawah ini.")
    
    tab_edit = st.tabs(["📘 Mata Kuliah", "👨‍🏫 Dosen", "👥 Kelas", "🏫 Ruangan"])
    
    # === TAB MATA KULIAH ===
    with tab_edit[0]:  # Mata Kuliah
        file = DATA_DIR / "matkul.csv"

        # Inisialisasi session state untuk edit
        if "edit_matkul_data" not in st.session_state:
            st.session_state.edit_matkul_data = None

        # Form Tambah Data
        with st.form("form_matkul"):
            # Jika ada data untuk diedit, isi form dengan data tersebut
            if st.session_state.edit_matkul_data is not None:
                edit_data = st.session_state.edit_matkul_data
                kode = st.text_input("Kode Mata Kuliah", value=edit_data["kode"])
                nama = st.text_input("Nama Mata Kuliah", value=edit_data["nama"])
                sks = st.number_input("Jumlah SKS", min_value=1, max_value=6, step=1, value=int(edit_data["sks"]))
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("💾 Update Mata Kuliah")
                with col2:
                    cancel = st.form_submit_button("❌ Batal Edit")
            else:
                kode = st.text_input("Kode Mata Kuliah")
                nama = st.text_input("Nama Mata Kuliah")
                sks = st.number_input("Jumlah SKS", min_value=1, max_value=6, step=1)
                submit = st.form_submit_button("Tambah Mata Kuliah")
                cancel = False

            if cancel:
                st.session_state.edit_matkul_data = None
                st.rerun()

            if submit:
                if st.session_state.edit_matkul_data is not None:
                    # Mode Update
                    if file.exists():
                        df_matkul = pd.read_csv(file)
                        edit_idx = st.session_state.edit_matkul_data["index"]
                        df_matkul.at[edit_idx, "kode_matkul"] = kode
                        df_matkul.at[edit_idx, "nama_matkul"] = nama
                        df_matkul.at[edit_idx, "sks"] = sks
                        df_matkul.to_csv(file, index=False)
                        st.success("✅ Mata kuliah berhasil diupdate!")
                        st.session_state.edit_matkul_data = None
                        st.rerun()
                else:
                    # Mode Tambah (kode asli Anda)
                    new_data = pd.DataFrame([[kode, nama, sks]], columns=["kode_matkul", "nama_matkul", "sks"])
                    if file.exists():
                        df_matkul = pd.read_csv(file)
                        df_matkul = pd.concat([df_matkul, new_data], ignore_index=True)
                    else:
                        df_matkul = new_data
                    df_matkul.to_csv(file, index=False)
                    st.success("✅ Mata kuliah berhasil ditambahkan!")
                    st.rerun()

        # === Tampilkan & Edit Data yang Ada ===
        if file.exists():
            df_matkul = pd.read_csv(file)
            st.markdown("### 🧾 Daftar Mata Kuliah")

            for idx, row in df_matkul.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 4, 2, 1, 1])
                with col1:
                    st.text(row["kode_matkul"])
                with col2:
                    st.text(row["nama_matkul"])
                with col3:
                    st.text(str(row["sks"]))
                with col4:
                    if st.button("✏️", key=f"edit_{idx}"):
                        # Set data untuk edit
                        st.session_state.edit_matkul_data = {
                            "index": idx,
                            "kode": row["kode_matkul"],
                            "nama": row["nama_matkul"],
                            "sks": row["sks"]
                        }
                        st.rerun()
                with col5:
                    if st.button("🗑️", key=f"hapus_{idx}"):
                        df_matkul.drop(index=idx, inplace=True)
                        df_matkul.reset_index(drop=True, inplace=True)
                        df_matkul.to_csv(file, index=False)
                        st.rerun()

    # === TAB DOSEN ===
    with tab_edit[1]:
        file = DATA_DIR / "dosen.csv"

        # Inisialisasi session state untuk edit dosen
        if "edit_dosen_data" not in st.session_state:
            st.session_state.edit_dosen_data = None

        # Form Tambah/Edit Data Dosen
        with st.form("form_dosen"):
            # Jika ada data untuk diedit, isi form dengan data tersebut
            if st.session_state.edit_dosen_data is not None:
                edit_data = st.session_state.edit_dosen_data
                col1, col2 = st.columns(2)
                with col1:
                    kode = st.text_input("Kode Dosen", value=edit_data["kode"])
                    nama = st.text_input("Nama Dosen", value=edit_data["nama"])
                with col2:
                    hari = st.multiselect("Preferensi Hari", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"], 
                                        default=edit_data["hari"] if edit_data["hari"] else [])
                    sesi = st.multiselect("Preferensi Sesi", [1, 2, 3, 4, 5], 
                                        default=edit_data["sesi"] if edit_data["sesi"] else [])
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("💾 Update Dosen")
                with col2:
                    cancel = st.form_submit_button("❌ Batal Edit")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    kode = st.text_input("Kode Dosen")
                    nama = st.text_input("Nama Dosen")
                with col2:
                    hari = st.multiselect("Preferensi Hari", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"])
                    sesi = st.multiselect("Preferensi Sesi", [1, 2, 3, 4, 5])
                submit = st.form_submit_button("➕ Tambah Dosen")
                cancel = False

            if cancel:
                st.session_state.edit_dosen_data = None
                st.rerun()

            if submit:
                if st.session_state.edit_dosen_data is not None:
                    # Mode Update
                    if file.exists():
                        df_dosen = pd.read_csv(file)
                        edit_idx = st.session_state.edit_dosen_data["index"]
                        df_dosen.at[edit_idx, "kode_dosen"] = kode
                        df_dosen.at[edit_idx, "nama_dosen"] = nama
                        df_dosen.at[edit_idx, "preferensi_hari"] = ",".join(hari)
                        df_dosen.at[edit_idx, "preferensi_sesi"] = ",".join(map(str, sesi))
                        df_dosen.to_csv(file, index=False)
                        st.success("✅ Dosen berhasil diupdate!")
                        st.session_state.edit_dosen_data = None
                        st.rerun()
                else:
                    # Mode Tambah
                    if kode and nama:
                        new_data = pd.DataFrame([[kode, nama, ",".join(hari), ",".join(map(str, sesi))]],
                                              columns=["kode_dosen", "nama_dosen", "preferensi_hari", "preferensi_sesi"])
                        if file.exists():
                            df_dosen = pd.read_csv(file)
                            df_dosen = pd.concat([df_dosen, new_data], ignore_index=True)
                        else:
                            df_dosen = new_data
                        df_dosen.to_csv(file, index=False)
                        st.success("✅ Dosen berhasil ditambahkan!")
                        st.rerun()

        # === Tampilkan & Edit Data yang Ada ===
        if file.exists():
            df_dosen = pd.read_csv(file)
            st.markdown("### 🧾 Daftar Dosen")

            for idx, row in df_dosen.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 2, 2, 1, 1])
                with col1:
                    st.text(row["kode_dosen"])
                with col2:
                    st.text(row["nama_dosen"])
                with col3:
                    st.text(str(row["preferensi_hari"]))
                with col4:
                    st.text(str(row["preferensi_sesi"]))
                with col5:
                    if st.button("✏️", key=f"edit_dosen_{idx}"):
                        # Set data untuk edit
                        hari_list = str(row["preferensi_hari"]).split(",") if pd.notna(row["preferensi_hari"]) and str(row["preferensi_hari"]) != "" else []
                        sesi_list = [int(x) for x in str(row["preferensi_sesi"]).split(",") if x.strip()] if pd.notna(row["preferensi_sesi"]) and str(row["preferensi_sesi"]) != "" else []
                        
                        st.session_state.edit_dosen_data = {
                            "index": idx,
                            "kode": row["kode_dosen"],
                            "nama": row["nama_dosen"],
                            "hari": hari_list,
                            "sesi": sesi_list
                        }
                        st.rerun()
                with col6:
                    if st.button("🗑️", key=f"hapus_dosen_{idx}"):
                        df_dosen.drop(index=idx, inplace=True)
                        df_dosen.reset_index(drop=True, inplace=True)
                        df_dosen.to_csv(file, index=False)
                        st.rerun()

    # === TAB KELAS ===
    with tab_edit[2]:
        file = DATA_DIR / "kelas.csv"

        # Inisialisasi session state untuk edit kelas
        if "edit_kelas_data" not in st.session_state:
            st.session_state.edit_kelas_data = None

        # Form Tambah/Edit Data Kelas
        with st.form("form_kelas"):
            # Jika ada data untuk diedit, isi form dengan data tersebut
            if st.session_state.edit_kelas_data is not None:
                edit_data = st.session_state.edit_kelas_data
                kode = st.text_input("Kode Kelas", value=edit_data["kode"])
                jumlah = st.number_input("Jumlah Mahasiswa", min_value=1, step=1, value=int(edit_data["jumlah"]))
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("💾 Update Kelas")
                with col2:
                    cancel = st.form_submit_button("❌ Batal Edit")
            else:
                kode = st.text_input("Kode Kelas")
                jumlah = st.number_input("Jumlah Mahasiswa", min_value=1, step=1)
                submit = st.form_submit_button("➕ Tambah Kelas")
                cancel = False

            if cancel:
                st.session_state.edit_kelas_data = None
                st.rerun()

            if submit:
                if st.session_state.edit_kelas_data is not None:
                    # Mode Update
                    if file.exists():
                        df_kelas = pd.read_csv(file)
                        edit_idx = st.session_state.edit_kelas_data["index"]
                        df_kelas.at[edit_idx, "kode_kelas"] = kode
                        df_kelas.at[edit_idx, "jumlah_mahasiswa"] = jumlah
                        df_kelas.to_csv(file, index=False)
                        st.success("✅ Kelas berhasil diupdate!")
                        st.session_state.edit_kelas_data = None
                        st.rerun()
                else:
                    # Mode Tambah
                    if kode:
                        new_data = pd.DataFrame([[kode, jumlah]], columns=["kode_kelas", "jumlah_mahasiswa"])
                        if file.exists():
                            df_kelas = pd.read_csv(file)
                            df_kelas = pd.concat([df_kelas, new_data], ignore_index=True)
                        else:
                            df_kelas = new_data
                        df_kelas.to_csv(file, index=False)
                        st.success("✅ Kelas berhasil ditambahkan!")
                        st.rerun()

        # === Tampilkan & Edit Data yang Ada ===
        if file.exists():
            df_kelas = pd.read_csv(file)
            st.markdown("### 🧾 Daftar Kelas")

            for idx, row in df_kelas.iterrows():
                col1, col2, col3, col4 = st.columns([3, 3, 1, 1])
                with col1:
                    st.text(row["kode_kelas"])
                with col2:
                    st.text(str(row["jumlah_mahasiswa"]))
                with col3:
                    if st.button("✏️", key=f"edit_kelas_{idx}"):
                        # Set data untuk edit
                        st.session_state.edit_kelas_data = {
                            "index": idx,
                            "kode": row["kode_kelas"],
                            "jumlah": row["jumlah_mahasiswa"]
                        }
                        st.rerun()
                with col4:
                    if st.button("🗑️", key=f"hapus_kelas_{idx}"):
                        df_kelas.drop(index=idx, inplace=True)
                        df_kelas.reset_index(drop=True, inplace=True)
                        df_kelas.to_csv(file, index=False)
                        st.rerun()

    # === TAB RUANGAN ===
    with tab_edit[3]:
        file = DATA_DIR / "ruangan.csv"

        # Inisialisasi session state untuk edit ruangan
        if "edit_ruangan_data" not in st.session_state:
            st.session_state.edit_ruangan_data = None

        # Form Tambah/Edit Data Ruangan
        with st.form("form_ruangan"):
            # Jika ada data untuk diedit, isi form dengan data tersebut
            if st.session_state.edit_ruangan_data is not None:
                edit_data = st.session_state.edit_ruangan_data
                col1, col2 = st.columns(2)
                with col1:
                    kode = st.text_input("Kode Ruangan", value=edit_data["kode"])
                    kapasitas = st.number_input("Kapasitas", min_value=1, step=1, value=int(edit_data["kapasitas"]))
                with col2:
                    hari_opsi = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
                    sesi_opsi = [1, 2, 3, 4, 5]

                    default_hari = [h for h in edit_data["hari"] if h in hari_opsi] if edit_data["hari"] else []
                    default_sesi = [s for s in edit_data["sesi"] if s in sesi_opsi] if edit_data["sesi"] else []

                    hari = st.multiselect("Hari Tersedia", hari_opsi, default=default_hari)
                    sesi = st.multiselect("Sesi Tersedia", sesi_opsi, default=default_sesi)
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("💾 Update Ruangan")
                with col2:
                    cancel = st.form_submit_button("❌ Batal Edit")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    kode = st.text_input("Kode Ruangan")
                    kapasitas = st.number_input("Kapasitas", min_value=1, step=1)
                with col2:
                    hari = st.multiselect("Hari Tersedia", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"])
                    sesi = st.multiselect("Sesi Tersedia", [1, 2, 3, 4, 5])
                submit = st.form_submit_button("➕ Tambah Ruangan")
                cancel = False

            if cancel:
                st.session_state.edit_ruangan_data = None
                st.rerun()

            if submit:
                if st.session_state.edit_ruangan_data is not None:
                    # Mode Update
                    if file.exists():
                        df_ruangan = pd.read_csv(file)
                        edit_idx = st.session_state.edit_ruangan_data["index"]
                        df_ruangan.at[edit_idx, "kode_ruang"] = kode
                        df_ruangan.at[edit_idx, "kapasitas"] = kapasitas
                        df_ruangan.at[edit_idx, "tersedia_hari"] = ",".join(hari)
                        df_ruangan.at[edit_idx, "tersedia_sesi"] = ",".join(map(str, sesi))
                        df_ruangan.to_csv(file, index=False)
                        st.success("✅ Ruangan berhasil diupdate!")
                        st.session_state.edit_ruangan_data = None
                        st.rerun()
                else:
                    # Mode Tambah
                    if kode:
                        new_data = pd.DataFrame([[kode, kapasitas, ",".join(hari), ",".join(map(str, sesi))]],
                                              columns=["kode_ruang", "kapasitas", "tersedia_hari", "tersedia_sesi"])
                        if file.exists():
                            df_ruangan = pd.read_csv(file)
                            df_ruangan = pd.concat([df_ruangan, new_data], ignore_index=True)
                        else:
                            df_ruangan = new_data
                        df_ruangan.to_csv(file, index=False)
                        st.success("✅ Ruangan berhasil ditambahkan!")
                        st.rerun()

        # === Tampilkan & Edit Data yang Ada ===
        if file.exists():
            df_ruangan = pd.read_csv(file)
            st.markdown("### 🧾 Daftar Ruangan")

            for idx, row in df_ruangan.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 1, 1])
                with col1:
                    st.text(row["kode_ruang"])
                with col2:
                    st.text(str(row["kapasitas"]))
                with col3:
                    st.text(str(row["tersedia_hari"]))
                with col4:
                    st.text(str(row["tersedia_sesi"]))
                with col5:
                    if st.button("✏️", key=f"edit_ruangan_{idx}"):
                        # Set data untuk edit
                        hari_list = str(row["tersedia_hari"]).split(",") if pd.notna(row["tersedia_hari"]) and str(row["tersedia_hari"]) != "" else []
                        sesi_list = [int(x) for x in str(row["tersedia_sesi"]).split(",") if x.strip()] if pd.notna(row["tersedia_sesi"]) and str(row["tersedia_sesi"]) != "" else []
                        
                        st.session_state.edit_ruangan_data = {
                            "index": idx,
                            "kode": row["kode_ruang"],
                            "kapasitas": row["kapasitas"],
                            "hari": hari_list,
                            "sesi": sesi_list
                        }
                        st.rerun()
                with col6:
                    if st.button("🗑️", key=f"hapus_ruangan_{idx}"):
                        df_ruangan.drop(index=idx, inplace=True)
                        df_ruangan.reset_index(drop=True, inplace=True)
                        df_ruangan.to_csv(file, index=False)
                        st.rerun()

# === MENU 3: JADWAL & RESET === (Bagian yang diperbaiki untuk main.py)
elif menu == "🔄 Jadwal & Reset":
    st.header("🔄 Jadwal Otomatis & Reset")
    
    # Cek ketersediaan data
    files_exist = {
        "matkul": (DATA_DIR / "matkul.csv").exists(),
        "dosen": (DATA_DIR / "dosen.csv").exists(),
        "kelas": (DATA_DIR / "kelas.csv").exists(),
        "ruangan": (DATA_DIR / "ruangan.csv").exists()
    }
    
    missing_files = [name for name, exists in files_exist.items() if not exists]
    
    if missing_files:
        st.error(f"❌ Data tidak lengkap! File yang hilang: {', '.join(missing_files)}")
        st.info("💡 Silakan upload semua file CSV terlebih dahulu di menu **Upload Data CSV** atau tambahkan data di menu **Edit Data**.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔁 Reset Jadwal")
        st.markdown("Hapus jadwal yang sudah ada dari layar dan file.")
        if st.button("🔁 Reset Jadwal", use_container_width=True):
            # Hapus dari session state
            if "jadwal" in st.session_state:
                del st.session_state["jadwal"]
            # Hapus file jadwal
            if JADWAL_PATH.exists():
                JADWAL_PATH.unlink()
            st.success("✅ Jadwal berhasil direset dan dihapus dari layar!")
            st.rerun()

    with col2:
        st.subheader("🤖 Jadwal Otomatis")
        st.markdown("Buat jadwal kuliah otomatis berdasarkan data yang tersedia.")
        
        # Disable button jika data tidak lengkap
        disabled = bool(missing_files)
        
        if st.button("🔄 Jadwalkan Otomatis", use_container_width=True, disabled=disabled):
            try:
                # Load data dengan error handling yang lebih baik
                with st.spinner("📊 Memuat data..."):
                    matkul, dosen, kelas, ruangan = load_all_data()
                
                # Validasi data
                if matkul.empty:
                    st.error("❌ Data mata kuliah kosong!")
                elif dosen.empty:
                    st.error("❌ Data dosen kosong!")
                elif kelas.empty:
                    st.error("❌ Data kelas kosong!")
                elif ruangan.empty:
                    st.error("❌ Data ruangan kosong!")
                else:
                    # Tampilkan informasi data yang akan diproses
                    st.info(f"📋 Data yang akan diproses: {len(matkul)} mata kuliah, {len(dosen)} dosen, {len(kelas)} kelas, {len(ruangan)} ruangan")
                    
                    # Cek apakah mata kuliah memiliki kolom yang diperlukan
                    required_matkul_cols = ['kode_matkul', 'nama_matkul', 'sks']
                    missing_matkul_cols = [col for col in required_matkul_cols if col not in matkul.columns]
                    
                    if missing_matkul_cols:
                        st.error(f"❌ Kolom yang hilang di data mata kuliah: {', '.join(missing_matkul_cols)}")
                    else:
                        # PENTING: Tambahkan kolom kelas dan dosen jika tidak ada
                        if 'kelas' not in matkul.columns:
                            # Jika tidak ada kolom kelas, buat mapping otomatis
                            kelas_list = kelas['kode_kelas'].tolist()
                            matkul['kelas'] = [kelas_list[i % len(kelas_list)] for i in range(len(matkul))]
                            st.warning("⚠️ Kolom 'kelas' tidak ditemukan di data mata kuliah. Menggunakan mapping otomatis.")
                        
                        if 'dosen' not in matkul.columns:
                            # Jika tidak ada kolom dosen, buat mapping otomatis
                            dosen_list = dosen['kode_dosen'].tolist()
                            matkul['dosen'] = [dosen_list[i % len(dosen_list)] for i in range(len(matkul))]
                            st.warning("⚠️ Kolom 'dosen' tidak ditemukan di data mata kuliah. Menggunakan mapping otomatis.")
                        
                        with st.spinner("🔄 Membuat jadwal..."):
                            df_jadwal = jadwalkan(matkul, dosen, kelas, ruangan)
                        
                        if not df_jadwal.empty:
                            st.session_state["jadwal"] = df_jadwal
                            st.success(f"✅ Jadwal berhasil dibuat dengan {len(df_jadwal)} mata kuliah terjadwal!")
                            st.rerun()
                        else:
                            st.error("❌ Tidak ada mata kuliah yang berhasil dijadwalkan. Periksa kembali data Anda.")
                            st.info("""
                            **Kemungkinan penyebab:**
                            - Kapasitas ruangan terlalu kecil untuk jumlah mahasiswa
                            - Preferensi dosen tidak cocok dengan ketersediaan ruangan
                            - Konflik jadwal yang tidak dapat diselesaikan
                            """)
                
            except FileNotFoundError as e:
                st.error(f"❌ File tidak ditemukan: {e}")
                st.info("💡 Pastikan semua file CSV sudah diupload di menu **Upload Data CSV**.")
            except Exception as e:
                st.error(f"❌ Error saat menjadwalkan: {str(e)}")
                st.info("💡 Periksa kembali format data CSV Anda.")
                
                # Tampilkan detail error untuk debugging
                with st.expander("🔍 Detail Error (untuk debugging)"):
                    st.code(str(e))

    # === TAMPILKAN JADWAL JIKA ADA ===
    st.markdown("---")
    
    if "jadwal" in st.session_state:
        st.subheader("📋 Jadwal Kuliah")
        df_jadwal = st.session_state["jadwal"]
        
        # Tampilkan ringkasan
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Mata Kuliah", len(df_jadwal))
        with col2:
            st.metric("👨‍🏫 Dosen", df_jadwal['dosen'].nunique())
        with col3:
            st.metric("🏫 Ruangan", df_jadwal['ruangan'].nunique())
        with col4:
            st.metric("👥 Kelas", df_jadwal['kelas'].nunique())
        
        # Tampilkan tabel jadwal
        st.dataframe(df_jadwal, use_container_width=True)
        
        # Tombol Download Jadwal
        col1, col2 = st.columns([3, 1])
        with col2:
            st.download_button(
                label="⬇️ Download CSV",
                data=df_jadwal.to_csv(index=False),
                file_name="jadwal_kuliah.csv",
                mime="text/csv",
                use_container_width=True
            )
        
    elif JADWAL_PATH.exists():
        try:
            df_jadwal = pd.read_csv(JADWAL_PATH)
            st.session_state["jadwal"] = df_jadwal
            st.subheader("📋 Jadwal Kuliah (dari file)")
            
            # Tampilkan ringkasan
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📚 Mata Kuliah", len(df_jadwal))
            with col2:
                st.metric("👨‍🏫 Dosen", df_jadwal['dosen'].nunique())
            with col3:
                st.metric("🏫 Ruangan", df_jadwal['ruang'].nunique())
            with col4:
                st.metric("👥 Kelas", df_jadwal['kelas'].nunique())
            
            st.dataframe(df_jadwal, use_container_width=True)
            
            # Tombol Download Jadwal
            col1, col2 = st.columns([3, 1])
            with col2:
                st.download_button(
                    label="⬇️ Download CSV",
                    data=df_jadwal.to_csv(index=False),
                    file_name="jadwal_kuliah.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"❌ Error membaca file jadwal: {e}")
            if st.button("🗑️ Hapus File Jadwal Corrupt"):
                JADWAL_PATH.unlink()
                st.success("✅ File jadwal yang corrupt telah dihapus.")
                st.rerun()
    else:
        st.info("💡 Belum ada jadwal yang dibuat. Silakan buat jadwal otomatis terlebih dahulu.")

# === FOOTER INFO ===
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Status Data")

# Cek ketersediaan file
files_status = {
    "Mata Kuliah": (DATA_DIR / "matkul.csv").exists(),
    "Dosen": (DATA_DIR / "dosen.csv").exists(),
    "Kelas": (DATA_DIR / "kelas.csv").exists(),
    "Ruangan": (DATA_DIR / "ruangan.csv").exists()
}

for name, exists in files_status.items():
    if exists:
        st.sidebar.success(f"✅ {name}")
    else:
        st.sidebar.error(f"❌ {name}")