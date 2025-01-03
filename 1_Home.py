import pandas as pd
import plotly.express as px
import streamlit as st


# Set page configuration
st.set_page_config(
    page_title="📊Dashboard Evaluasi Teknik Informatika",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Menampilkan judul aplikasi di tengah
st.markdown("""
    <h2 style="text-align: center;">📊Dashboard Evaluasi Teknik Informatika </h2>
""", unsafe_allow_html=True)

st.divider()

# Fungsi untuk memuat data dari file CSV
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Gagal memuat data dari {file_path}: {e}")
        return pd.DataFrame()

# Fungsi untuk memuat data dengan multi-header
def load_data_with_multi_header(file_path):
    try:
        return pd.read_csv(file_path, header=[0, 1])  # Contoh untuk header multi-barisan
    except Exception as e:
        st.error(f"Gagal memuat data multi-header dari {file_path}: {e}")
        return pd.DataFrame()

# Memuat data untuk masing-masing kategori
data_c1_stt = load_data("C.1.SurveyPemahamanVisiMisiSTTWastukancana.csv")
data_c1_tif = load_data("C.1.SurveyPemahamanVisiMisiTIF.csv")
data_c2_dosen = load_data("C2.tatakeloladosendantendik-prep.csv")
data_c2_mhs = load_data_with_multi_header("C2.tatakelolamhs-preprossesing.csv")
data_c3 = load_data("C3.-layanan-mahasiswa-prep.csv")
data_c4_dosen = load_data_with_multi_header("C.4.KepuasanDosenterhadapSDM-prep.csv")
data_c4_tendik = load_data_with_multi_header("C.4.KepuasanTendikterhadapSDM-prep.csv")
data_c5_dosen = load_data("C5.saranadosen-prep.csv")
data_c5_mhs = load_data("C5.saranamahasiswa-prep.csv")
data_c5_tendik = load_data("C5.saranatendik-prep.csv")
data_c6_dosen = load_data("C.6.Kepuasandosen-prep.csv")
data_c6_tendik = load_data("C.6.Kepuasantendik-prep.csv")
data_c7 = load_data("penelitian-prep.csv")
data_c8 = load_data("pengabdian-prep.csv")

# Fungsi untuk memproses data kategori C1
def process_c1(data_stt, data_tif):
    # Contoh: Menghitung distribusi Faham dan Tidak Faham
    def calculate_understanding(data, label):
        non_neutral_data = data[data.apply(lambda row: ~row.isin([3]), axis=1)]
        understanding_count = {
            "Tidak Faham": ((non_neutral_data == 1) | (non_neutral_data == 2)).sum().sum(),
            "Faham": ((non_neutral_data == 4) | (non_neutral_data == 5)).sum().sum(),
        }
        total = sum(understanding_count.values())
        return pd.DataFrame({
            'Kategori': understanding_count.keys(),
            'Jumlah': understanding_count.values(),
            'Persentase': [count / total * 100 for count in understanding_count.values()],
            'Sumber': label
        })
    
    df_stt = calculate_understanding(data_stt, "STT Wastukancana")
    df_tif = calculate_understanding(data_tif, "TIF")
    return pd.concat([df_stt, df_tif], ignore_index=True)


# Fungsi untuk memproses data kategori C2 (dosen, tendik, mahasiswa)
def process_c2(data_dosen_tendik, data_mhs):
    # Pastikan data numerik
    data_dosen_tendik = data_dosen_tendik.apply(pd.to_numeric, errors='coerce')
    data_mhs = data_mhs.apply(pd.to_numeric, errors='coerce')

    # Proses data Dosen & Tendik (nilai 1, 2, 4, 5)
    non_neutral_data_dosen_tendik = data_dosen_tendik[data_dosen_tendik.apply(lambda row: ~row.isin([3]), axis=1)]
    
    # Hitung jumlah kategori untuk Dosen&Tendik
    categories_count_dosen_tendik = {
        "Puas": (non_neutral_data_dosen_tendik >= 4).sum().sum(),
        "Tidak Puas": (non_neutral_data_dosen_tendik <= 2).sum().sum(),
    }

    # Proses data Mahasiswa
    non_neutral_data_mhs = data_mhs[data_mhs.apply(lambda row: ~row.isin([3]), axis=1)]
    
    # Hitung jumlah kategori untuk Mahasiswa
    categories_count_mhs = {
        "Puas": (non_neutral_data_mhs >= 4).sum().sum(),
        "Tidak Puas": (non_neutral_data_mhs <= 2).sum().sum(),
    }

    # Gabungkan data Dosen&Tendik dan Mahasiswa
    combined_categories_count = {
        "Puas": categories_count_dosen_tendik["Puas"] + categories_count_mhs["Puas"],
        "Tidak Puas": categories_count_dosen_tendik["Tidak Puas"] + categories_count_mhs["Tidak Puas"],
    }

    # Hitung total kategori
    total_responses = sum(combined_categories_count.values())

    # Persentase
    fulfillment_data = pd.DataFrame({
        'Kategori': combined_categories_count.keys(),
        'Jumlah': combined_categories_count.values(),
        'Persentase': [count / total_responses * 100 for count in combined_categories_count.values()]
    })

    return fulfillment_data

# Fungsi untuk memproses data kategori C3
def process_c3(data):
    # Filter data tanpa netral (skor == 3 dianggap netral)
    non_neutral_data = data[data.apply(lambda row: ~row.isin([3]), axis=1)]

    # Hitung jumlah kategori Puas dan Tidak Puas
    categories_count = {
        "Puas": (non_neutral_data >= 4).sum().sum(),  # Skor 4 dan 5
        "Tidak Puas": (non_neutral_data <= 2).sum().sum(),  # Skor 1 dan 2
    }

    # Hitung total jawaban yang relevan (tanpa netral)
    total_non_neutral = sum(categories_count.values())

    # Hitung persentase untuk setiap kategori
    fulfillment_data = pd.DataFrame({
        'Status': categories_count.keys(),
        'Jumlah': categories_count.values(),
        'Persentase': [count / total_non_neutral * 100 for count in categories_count.values()]
    })

    return fulfillment_data
  

# Fungsi untuk memproses data kategori C4
def process_c4(data_dosen, data_tendik):
    # Fungsi untuk menghitung distribusi kepuasan
    def calculate_satisfaction(data, label):
        try:
            satisfaction_count = {
                "Tidak Puas": ((data == 1) | (data == 2)).sum().sum(),
                "Puas": ((data == 4) | (data == 5)).sum().sum(),
            }
            total = sum(satisfaction_count.values())
            if total == 0:  # Menghindari pembagian dengan nol
                return pd.DataFrame(columns=["Kategori", "Jumlah", "Persentase", "Sumber"])
            return pd.DataFrame({
                'Kategori': satisfaction_count.keys(),
                'Jumlah': satisfaction_count.values(),
                'Persentase': [count / total * 100 for count in satisfaction_count.values()],
                'Sumber': label
            })
        except Exception as e:
            st.error(f"Error dalam menghitung kepuasan untuk {label}: {e}")
            return pd.DataFrame(columns=["Kategori", "Jumlah", "Persentase", "Sumber"])

    df_dosen = calculate_satisfaction(data_dosen, "Dosen")
    df_tendik = calculate_satisfaction(data_tendik, "Tendik")
    return pd.concat([df_dosen, df_tendik], ignore_index=True)


# Fungsi untuk memproses data kategori C5 (Dosen, Mahasiswa, Tendik)
def process_c5(data_dosen, data_mhs, data_tendik):
    # Fungsi untuk menghitung kategori Puas dan Tidak Puas
    def calculate_satisfaction(data):
        # Filter data tanpa netral (skor == 3 dianggap netral)
        non_neutral_data = data[data.apply(lambda row: ~row.isin([3]), axis=1)]

        # Hitung jumlah kategori Puas dan Tidak Puas
        categories_count = {
            "Puas": (non_neutral_data >= 4).sum().sum(),  # Skor 4 dan 5
            "Tidak Puas": (non_neutral_data <= 2).sum().sum(),  # Skor 1 dan 2
        }

        # Hitung total jawaban yang relevan (tanpa netral)
        total_non_neutral = sum(categories_count.values())

        # Hitung persentase untuk setiap kategori
        satisfaction_data = pd.DataFrame({
            'Status': categories_count.keys(),
            'Jumlah': categories_count.values(),
            'Persentase': [count / total_non_neutral * 100 for count in categories_count.values()]
        })

        return satisfaction_data

    # Proses data untuk masing-masing kategori
    dosen_satisfaction = calculate_satisfaction(data_dosen)
    mhs_satisfaction = calculate_satisfaction(data_mhs)
    tendik_satisfaction = calculate_satisfaction(data_tendik)

    # Gabungkan semua data menjadi satu
    combined_satisfaction = pd.concat([dosen_satisfaction, mhs_satisfaction, tendik_satisfaction], ignore_index=True)

    return combined_satisfaction

# Fungsi untuk memproses data kategori C6
def process_c6(data):
    # Filter data tanpa netral (skor == 3 dianggap netral)
    non_neutral_data = data[data.apply(lambda row: ~row.isin([3]), axis=1)]

    # Hitung jumlah kategori
    categories_count = {
        "Sangat Kurang": (non_neutral_data == 1).sum().sum(),
        "Kurang": (non_neutral_data == 2).sum().sum(),
        "Baik": (non_neutral_data == 4).sum().sum(),
        "Sangat Baik": (non_neutral_data == 5).sum().sum(),
    }

    return categories_count

# Proses data untuk Dosen dan Tendik
categories_count_dosen = process_c6(data_c6_dosen)
categories_count_tendik = process_c6(data_c6_tendik)

# Gabungkan hasil kategori dari kedua dataset
combined_categories_count = {
    category: categories_count_dosen.get(category, 0) + categories_count_tendik.get(category, 0)
    for category in set(categories_count_dosen.keys()).union(categories_count_tendik.keys())
}

# Hitung total jawaban yang relevan
total_combined = sum(combined_categories_count.values())

# Hitung persentase untuk setiap kategori
fulfillment_data_combined = pd.DataFrame({
    'Kategori': combined_categories_count.keys(),
    'Jumlah': combined_categories_count.values(),
    'Persentase': [count / total_combined * 100 for count in combined_categories_count.values()]
})

# Buat diagram pie untuk distribusi gabungan
fig_combined_donut = px.pie(
    fulfillment_data_combined,
    values='Persentase',
    names='Kategori',
    hole=0.5,
    title="Pendidikan",
    color_discrete_sequence=px.colors.sequential.Purpor
)

# Update layout untuk menyesuaikan tampilan
fig_combined_donut.update_layout(
    title_x=0.35,  # Memusatkan judul
    legend_title="Kategori",  # Judul untuk legenda
    legend_orientation="h",  # Legend secara horizontal
    legend_yanchor="bottom",  # Menyelaraskan legend di bagian bawah
    legend_y=-0.3,  # Memindahkan legend ke bawah chart
    legend_x=0.5,  # Memusatkan legend secara horizontal
    legend_xanchor="center",  # Memastikan legend ter-anchor di tengah
    height=350,
    width=600
)


# Fungsi untuk memproses data kategori C7 (Penelitian)
def process_c7(data):
    # Filter data tanpa netral (skor == 3 dianggap netral)
    non_neutral_data = data[data.apply(lambda row: ~row.isin([3]), axis=1)]

    # Hitung jumlah kategori Puas dan Tidak Puas
    categories_count = {
        "Puas": (non_neutral_data >= 4).sum().sum(),  # Skor 4 dan 5
        "Tidak Puas": (non_neutral_data <= 2).sum().sum(),  # Skor 1 dan 2
    }

    # Hitung total jawaban yang relevan (tanpa netral)
    total_non_neutral = sum(categories_count.values())

    # Hitung persentase untuk setiap kategori
    satisfaction_data = pd.DataFrame({
        'Status': categories_count.keys(),
        'Jumlah': categories_count.values(),
        'Persentase': [count / total_non_neutral * 100 for count in categories_count.values()]
    })

    return satisfaction_data

# Fungsi untuk memproses data kategori C8 (Pengabdian)
def process_c8(data):
    # Filter data tanpa netral (skor == 3 dianggap netral)
    non_neutral_data = data[data.apply(lambda row: ~row.isin([3]), axis=1)]

    # Hitung jumlah kategori Puas dan Tidak Puas
    categories_count = {
        "Puas": (non_neutral_data >= 4).sum().sum(),  # Skor 4 dan 5
        "Tidak Puas": (non_neutral_data <= 2).sum().sum(),  # Skor 1 dan 2
    }

    # Hitung total jawaban yang relevan (tanpa netral)
    total_non_neutral = sum(categories_count.values())

    # Hitung persentase untuk setiap kategori
    satisfaction_data = pd.DataFrame({
        'Status': categories_count.keys(),
        'Jumlah': categories_count.values(),
        'Persentase': [count / total_non_neutral * 100 for count in categories_count.values()]
    })

    return satisfaction_data




# Membagi layout untuk tampilan Streamlit
c3, c5,c7,c8 = st.columns(4)
st.divider()
c2, c6 = st.columns([3, 3 ])
c1, c4 = st.columns([3, 3])

# Contoh penggunaan data (Tampilkan bentuk data jika diperlukan)
with c1:
    with st.container(border=True):
            # Proses data C1
        processed_c1 = process_c1(data_c1_stt, data_c1_tif)

        # Menampilkan grouped bar chart
        fig_c1 = px.bar(
            processed_c1,
            y="Kategori",  # Kategori pada sumbu x
            x="Persentase",  # Persentase pada sumbu y
            color="Sumber",  # Memisahkan berdasarkan 'Sumber'
            barmode="group",  # Menggunakan barmode 'group' untuk bar yang dikelompokkan
            title="Visi dan Misi STT Wastukancana & Teknik Informatika",
            color_discrete_sequence=px.colors.sequential.Purpor_r
        )

        fig_c1.update_layout(
            title_x=0.1,
            bargap=0.3,  # Jarak antar bar
            bargroupgap=0.2,  # Jarak antar bar dalam grup
            xaxis_title="Kategori",  # Menambahkan label pada sumbu x
            yaxis_title="Persentase", # Menambahkan label pada sumbu y
            height=400,
            width=600
        )

        st.plotly_chart(fig_c1, use_container_width=True)


# (Tampilkan data lainnya sesuai kebutuhan)
with c2:
    with st.container(border=True):

        processed_data_c2 = process_c2(data_c2_dosen, data_c2_mhs)
            # Membuat grafik pie chart
        fig_donut = px.pie(
            processed_data_c2,
            values='Persentase',
            names='Kategori',
            hole=0.5,
            title="Tata Kelola,Tata Pamong&Kerja Sama",
            color_discrete_sequence=px.colors.sequential.Purpor
        )

        # Memperbarui tata letak grafik
        fig_donut.update_layout(
            title_x=0.3,
            legend_title="Kategori",
            legend_orientation="h",
            legend_yanchor="bottom",
            legend_y=-0.3,
            legend_x=0.5,
            legend_xanchor="center",
            height=350,
            width=400
        )

        # Menampilkan grafik di Streamlit
        st.plotly_chart(fig_donut, use_container_width=True)


    

with c3:

    # Proses data C3 untuk mendapatkan kategori Puas dan Tidak Puas
    fulfillment_data_c3 = process_c3(data_c3)  # Pastikan data_c3 sudah terdefinisi sebelumnya

    # Ambil persentase kategori
    puas_percentage = fulfillment_data_c3.loc[fulfillment_data_c3['Status'] == 'Puas', 'Persentase'].values[0]
    tidak_puas_percentage = fulfillment_data_c3.loc[fulfillment_data_c3['Status'] == 'Tidak Puas', 'Persentase'].values[0]

    # Tampilkan progres bar dengan dua bagian
    st.markdown(f"""
        <div style="border: px solid; padding: 10px; border-radius: 15px; text-align: center;
                        background: linear-gradient(to right, #9b59b6, #f06292); 
                        border-image: linear-gradient(to right, #9b59b6, #f06292) 1;">
            <p style="font-size: 18px; margin: 0; color: black; ">Mahasiswa</p>
            <p style="font-size: 25px; margin: 5px 0; font-weight: bold; color: black;"> {puas_percentage:.2f}%</p>
            <p style="font-size: 16px; color: white; ">Puas: {puas_percentage:.2f}% | Tidak Puas: {tidak_puas_percentage:.2f}%</p>
            <div style="height: 10px; background-color: #d3d3d3; border-radius: 10px;">
            <div style="width: {puas_percentage}%; height: 100%; background-color: white; border-radius: 10px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)


with c5:

    # Proses data C5 untuk Dosen, Mahasiswa, dan Tendik
    fulfillment_data_c5 = process_c5(data_c5_dosen, data_c5_mhs, data_c5_tendik)

    # Ambil persentase kategori
    puas_percentage = fulfillment_data_c5.loc[fulfillment_data_c5['Status'] == 'Puas', 'Persentase'].values[0]
    tidak_puas_percentage = fulfillment_data_c5.loc[fulfillment_data_c5['Status'] == 'Tidak Puas', 'Persentase'].values[0]

    # Tampilkan progres bar dengan dua bagian
    st.markdown(f"""
        <div style="border: px solid; padding: 10px; border-radius: 15px; text-align: center;
                        background: linear-gradient(to right, #ff5733, #ff8c00);
                        border-image: linear-gradient(to right, #ff5733, #ff8c00) 1;">
            <p style="font-size: 18px; margin: 0; color: black; ">Keuangan, Sarana & Prasarana</p>
            <p style="font-size: 25px; margin: 5px 0; font-weight: bold; color: black;"> {puas_percentage:.2f}%</p>
            <p style="font-size: 16px; color: white; ">Puas: {puas_percentage:.2f}% | Tidak Puas: {tidak_puas_percentage:.2f}%</p>
            <div style="height: 10px; background-color: #d3d3d3; border-radius: 10px;">
            <div style="width: {puas_percentage}%; height: 100%; background-color: white; border-radius: 10px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with c6:
    with st.container(border=True):
        # Menampilkan diagram pie untuk gabungan Dosen dan Tendik
        st.plotly_chart(fig_combined_donut, use_container_width=True)

with c7:
    # Proses data C7 untuk Penelitian
    fulfillment_data_c7 = process_c7(data_c7)

    # Ambil persentase kategori
    puas_percentage = fulfillment_data_c7.loc[fulfillment_data_c7['Status'] == 'Puas', 'Persentase'].values[0]
    tidak_puas_percentage = fulfillment_data_c7.loc[fulfillment_data_c7['Status'] == 'Tidak Puas', 'Persentase'].values[0]

    # Tampilkan progres bar dengan dua bagian
    st.markdown(f"""
        <div style="border: 0px solid; padding: 10px; border-radius: 15px; text-align: center;
                        background: linear-gradient(to right, #00b0ff, #04c778); 
                        border-image: linear-gradient(to right, #00b0ff, #04c778) 1;">
            <p style="font-size: 18px; margin: 0; color: black; ">Penelitian</p>
            <p style="font-size: 25px; margin: 5px 0; font-weight: bold; color: black;"> {puas_percentage:.2f}%</p>
            <p style="font-size: 16px; color: white; ">Puas: {puas_percentage:.2f}% | Tidak Puas: {tidak_puas_percentage:.2f}%</p>
            <div style="height: 10px; background-color: #d3d3d3; border-radius: 10px;">
            <div style="width: {puas_percentage}%; height: 100%; background-color: white; border-radius: 10px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with c8:
    
    # Proses data C8 untuk Pengabdian
    fulfillment_data_c8 = process_c8(data_c8)

    # Ambil persentase kategori
    puas_percentage = fulfillment_data_c8.loc[fulfillment_data_c8['Status'] == 'Puas', 'Persentase'].values[0]
    tidak_puas_percentage = fulfillment_data_c8.loc[fulfillment_data_c8['Status'] == 'Tidak Puas', 'Persentase'].values[0]

    # Tampilkan progres bar dengan dua bagian
    st.markdown(f"""
        <div style="border: 0px solid; padding: 10px; border-radius: 15px; text-align: center;
                        background: linear-gradient(to right, #fd1dd4, #32a4c9); 
                        border-image: linear-gradient(to right, #00b0ff, #04c778) 1;">
            <p style="font-size: 18px; margin: 0; color: black; ">Pengabdian Kepada Masyarakat</p>
            <p style="font-size: 25px; margin: 5px 0; font-weight: bold; color: black;"> {puas_percentage:.2f}%</p>
            <p style="font-size: 16px; color: white; ">Puas: {puas_percentage:.2f}% | Tidak Puas: {tidak_puas_percentage:.2f}%</p>
            <div style="height: 10px; background-color: #d3d3d3; border-radius: 10px;">
            <div style="width: {puas_percentage}%; height: 100%; background-color: white; border-radius: 10px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)  # Pastikan unsafe_allow_html=True

with c4:
    with st.container(border=True):
        # Proses data C4
        processed_c4 = process_c4(data_c4_dosen, data_c4_tendik)

                # Visualisasi grouped bar chart untuk C4
        fig_c4 = px.bar(
                    processed_c4,
                    x="Kategori",  # Kategori pada sumbu y
                    y="Persentase",  # Persentase pada sumbu x
                    color="Sumber",  # Memisahkan berdasarkan 'Sumber'
                    barmode="group",  # Menggunakan barmode 'group' untuk bar yang dikelompokkan
                    title="Kepuasan Dosen dan Tendik terhadap SDM",
                    color_discrete_sequence=px.colors.sequential.Purpor_r
                )

        fig_c4.update_layout(
                    title_x=0.15,
                    bargap=0.3,  # Jarak antar bar
                    bargroupgap=0.2,  # Jarak antar bar dalam grup
                    xaxis_title="Persentase",  # Menambahkan label pada sumbu x
                    yaxis_title="Kategori",  # Menambahkan label pada sumbu y
                    height=400,
                    width=600
                )

                # Menampilkan chart di Streamlit
        st.plotly_chart(fig_c4, use_container_width=True)
