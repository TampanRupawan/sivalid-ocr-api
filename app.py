import streamlit as st
import cv2
import numpy as np

from pipeline import TranscriptPipeline

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="OCR Validasi Transkrip",
    page_icon="🎓",
    layout="wide"
)

# =====================================================
# HEADER
# =====================================================

st.title("OCR Validasi Transkrip Nilai Mahasiswa")

st.divider()

# =====================================================
# LOAD PIPELINE
# =====================================================

pipeline = TranscriptPipeline()

# =====================================================
# SESSION STATE
# =====================================================

if "hasil" not in st.session_state:
    st.session_state.hasil = None


# =====================================================
# UPLOAD
# =====================================================

st.header("📤 Upload Transkrip")

uploaded_file = st.file_uploader(
    label="Pilih file transkrip nilai mahasiswa",
    type=["jpg", "jpeg", "png"],
    help="Format yang didukung : JPG, JPEG, PNG"
)

if uploaded_file is not None:

    # ==========================================
    # READ IMAGE
    # ==========================================

    file_bytes = np.asarray(
        bytearray(uploaded_file.read()),
        dtype=np.uint8
    )

    image = cv2.imdecode(
        file_bytes,
        cv2.IMREAD_COLOR
    )

    tinggi, lebar = image.shape[:2]

    st.divider()

    # ==========================================
    # FILE INFO + PREVIEW
    # ==========================================

    info_col, preview_col = st.columns(
        [1, 2],
        gap="large"
    )

    # -----------------------------
    # FILE INFO
    # -----------------------------

    with info_col:

        st.subheader("📋 Informasi File")

        st.metric(
            "📄 Nama File",
            uploaded_file.name
        )

        st.metric(
            "🖼 Format",
            uploaded_file.type.upper()
        )

        st.metric(
            "💾 Ukuran",
            f"{uploaded_file.size/(1024*1024):.2f} MB"
        )

        st.metric(
            "📐 Resolusi",
            f"{lebar} × {tinggi}"
        )

    # -----------------------------
    # PREVIEW
    # -----------------------------

    with preview_col:

        st.subheader("🖼 Preview Transkrip")

        st.image(
            cv2.cvtColor(
                image,
                cv2.COLOR_BGR2RGB
            ),
            width='stretch'
        )

    st.divider()

    # ==========================================
    # PROCESS BUTTON
    # ==========================================

    kiri, tengah, kanan = st.columns([2,1,2])

    with tengah:

        process = st.button(
            "PROCESS",
            width='stretch',
            type="primary"
        )

    if process:

        progress = st.progress(0)
        status = st.empty()
        status.info("🚀 Menjalankan Pipeline...")
        progress.progress(20)
        hasil = pipeline.run(image)
        progress.progress(100)
        status.success("✅ Pipeline selesai diproses.")
        st.session_state.hasil = hasil
        progress.empty()


# =====================================================
# HASIL
# =====================================================

if st.session_state.hasil is not None:

    hasil = st.session_state.hasil
    cer = hasil["CER"]
    st.divider()
    st.header("🎯 Hasil Deteksi")
    st.caption(
        "Visualisasi hasil deteksi area informasi akademik menggunakan model YOLOv8."
    )

    left, right = st.columns(
        [2.3, 1],
        gap="large"
    )

# =====================================================
# GAMBAR YOLO
# =====================================================

    with left:

        st.image(
            cv2.cvtColor(
                hasil["gambar"],
                cv2.COLOR_BGR2RGB
            ),
            width='stretch'
        )

    # =====================================================
    # IDENTITAS
    # =====================================================

    with right:

        st.subheader("👤 Identitas Mahasiswa")
        identitas = hasil["identitas"]

        st.metric(
            "👤 Nama",
            identitas.get("nama", "-")
        )

        st.metric(
            "🆔 NPM",
            identitas.get("npm", "-")
        )

        st.metric(
            "📈 IPK",
            identitas.get("ipk", "-")
        )

        st.metric(
            "📚 Total SKS",
            identitas.get("kredit", "-")
        )

# =====================================================
# PIPELINE RESULT
# =====================================================

    st.divider()
    st.header("📂 Hasil Pipeline")
    st.caption(
        "Hasil setiap tahapan mulai dari Cropping, OCR, Parsing, Database hingga Validasi."
    )

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "✂️ Crop",
        "🔍 OCR",
        "📄 Parser",
        "🗄 Database",
        "✅ Validation",
        "🖊️Evaluasi OCR"
    ])

    with tab1:

        st.subheader("✂️ Hasil Cropping")
        crops = hasil["crop"]
        if len(crops) == 0:

            st.warning("Tidak ada hasil cropping.")

        else:
            jumlah_kolom = 4
            for i in range(0, len(crops), jumlah_kolom):
                cols = st.columns(jumlah_kolom)

                for j, col in enumerate(cols):

                    if i + j >= len(crops):
                        break

                    item = crops[i + j]

                    with col:

                        st.markdown(
                            f"### {item['CLASS']}"
                        )

                        st.image(
                            cv2.cvtColor(
                                item["CROP"],
                                cv2.COLOR_BGR2RGB
                            ),
                            width='stretch'
                        )

                        st.caption(
                            f"Confidence : {item['CONFIDENCE']:.3f}"
                        )

    with tab2:

        st.subheader("🔍 Hasil OCR")

        st.caption(
            f"Jumlah data OCR : {len(hasil['ocr'])}"
        )

        st.dataframe(
            hasil["ocr"],
            width='stretch',
            hide_index=True
        )

    with tab3:

        st.subheader("📄 Hasil Parser")

        st.caption(
            f"Jumlah Mata Kuliah : {len(hasil['transkrip'])}"
        )

        df_parser = hasil["transkrip"].copy()
        df_parser.index = range(1, len(df_parser) + 1)

        st.dataframe(
            df_parser,
            width='stretch'
        )


    with tab4:

        st.subheader("🗄 Database Akademik")

        st.caption(
            f"Jumlah Data : {len(hasil['database'])}"
        )

        df_database = hasil["database"].copy()
        df_database.index = range(1, len(df_database) + 1)

        st.dataframe(
            df_database,
            width='stretch'
        )

    with tab5:

        st.subheader("✅ Hasil Validasi")

        st.caption(
            f"Jumlah Validasi : {len(hasil['validasi'])}"
        )

        df_validasi = hasil["validasi"].copy()
        df_validasi.index = range(1, len(df_validasi) + 1)

        st.dataframe(
            df_validasi,
            width='stretch'
        )

    with tab6:

        st.subheader("🖊️Evaluasi PaddleOCR")

        st.metric(
            "CER",
            f"{cer['CER']:.4f}"
        )

        st.metric(
            "Substitution",
            cer["Substitution"]
        )

        st.metric(
            "Deletion",
            cer["Deletion"]
        )

        st.metric(
            "Insertion",
            cer["Insertion"]
        )

        st.metric(
            "Ground Truth Characters",
            cer["Ground Truth Characters"]
        )


# =====================================================
# ACCURACY DASHBOARD
# =====================================================

    st.divider()

    st.header("📊 Accuracy Dashboard")

    st.caption(
        "Persentase keberhasilan sistem dalam melakukan validasi data akademik."
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            label="📘 Kode Mata Kuliah",
            value=f"{hasil['akurasi_kode']:.2f}%"
        )

    with c2:

        st.metric(
            label="📝 Nama Mata Kuliah",
            value=f"{hasil['akurasi_nama']:.2f}%"
        )

    with c3:

        st.metric(
            label="🎓 Huruf Mutu",
            value=f"{hasil['akurasi_hm']:.2f}%"
        )

    st.divider()
    
    st.subheader("Ground Truth")
    
    st.code(
        cer["Ground Truth"],
        language="text"
        )
    
    st.subheader("OCR Text")
    
    st.code(
        cer["OCR"],
        language="text"
        )