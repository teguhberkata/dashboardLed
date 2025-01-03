import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="📊Survey Evaluasi Tingkat Kepuasan Dosen Dan Tenaga Kependidikan Terhadap Sistem Pengelolaan SDM",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Menampilkan judul aplikasi di tengah
st.markdown("""
    <h2 style="text-align: center;">📊Survey Evaluasi Tingkat Kepuasan Dosen Dan Tenaga Kependidikan Terhadap Sistem Pengelolaan SDM
</h2>
""", unsafe_allow_html=True)

# Fungsi untuk memuat data dengan multi-header
def load_data_with_multi_header(file_path):
    data = pd.read_csv(file_path, header=[0, 1], encoding="utf-8")
    data.columns = ['_'.join(col).strip() for col in data.columns.values]
    return data

# Fungsi untuk menghitung rata-rata per kategori dan pertanyaan
def calculate_avg_score(data, kategori_column='kategori', score_column='nilai', pertanyaan_column='pertanyaan'):
    return data.groupby([kategori_column, pertanyaan_column])[score_column].mean().reset_index()


def calculate_avg_score_permanent(data, kategori_column='kategori', score_column='nilai'):
    if kategori_column not in data.columns or score_column not in data.columns:
        st.warning("Kolom 'kategori' atau 'nilai' tidak ditemukan dalam data.")
        return pd.DataFrame()
    
    # Drop NaN values untuk menghindari error
    data = data.dropna(subset=[kategori_column, score_column])
    return data.groupby(kategori_column)[score_column].mean().reset_index()


# Fungsi untuk memuat data dengan caching
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# Tampilkan deskripsi survei dan grafik
tab1, tab2 = st.tabs(["Survey Kepuasan Dosen (Pengajaran, Suasana Kerja, Penghargaan) - REV", "Survey Kepuasan Tendik (Kepemimpinan, Kepegawaian, Keuangan) - REV"])

with tab1 :
    # Load data
    file_path = "C.4.KepuasanDosenterhadapSDM-prep.csv"  # Ganti dengan path ke file Anda
    data = load_data_with_multi_header(file_path)  # Memuat data dengan multi-header

            # Pisahkan kategori dan nilai dari kolom multi-header
    data_long = data.melt(var_name='kolom_asli', value_name='nilai')

    # Ekstraksi kategori dan pertanyaan dari nama kolom
    data_long['kategori'] = data_long['kolom_asli'].str.split('_').str[0]
    data_long['pertanyaan'] = data_long['kolom_asli'].str.split('_').str[1]

    # Drop kolom yang tidak diperlukan
    data_long = data_long.drop(columns=['kolom_asli'])

    # Menghitung rata-rata nilai per kategori
    avg_scores_permanent = calculate_avg_score_permanent(data_long, kategori_column='kategori', score_column='nilai')


    # Inisialisasi session_state untuk semua filter jika belum ada
    if 'selected_kategori' not in st.session_state:
        st.session_state['selected_kategori'] = 'All'
    if 'selected_pertanyaan' not in st.session_state:
        st.session_state['selected_pertanyaan'] = 'All'

    # FILTER 1: Kategori
    kategori_list = ['All'] + sorted(data.columns.str.split('_').str[0].unique())  # Ambil kategori dari level pertama
    selected_kategori = st.selectbox(
        '🔎Pilih Kategori :',
        options=kategori_list,
        index=kategori_list.index(st.session_state['selected_kategori']) if st.session_state['selected_kategori'] in kategori_list else 0
    )
    st.session_state['selected_kategori'] = selected_kategori

    # Filter data berdasarkan Kategori yang dipilih
    if selected_kategori == 'All':
        filtered_data = data
    else:
        # Pilih kolom yang sesuai dengan kategori
        filtered_data = data.loc[:, data.columns.str.startswith(selected_kategori)]

    # FILTER 2: Pertanyaan
    pertanyaan_list = ['All'] + sorted(filtered_data.columns.str.split('_').str[1].unique())  # Ambil pertanyaan dari level kedua
    selected_pertanyaan = st.selectbox(
        '🔎Pilih Pertanyaan :',
        options=pertanyaan_list,
        index=pertanyaan_list.index(st.session_state['selected_pertanyaan']) if st.session_state['selected_pertanyaan'] in pertanyaan_list else 0
    )
    st.session_state['selected_pertanyaan'] = selected_pertanyaan

    # Filter data berdasarkan Pertanyaan yang dipilih
    if selected_pertanyaan == 'All':
        filtered_data = filtered_data
    else:
        # Pilih kolom yang sesuai dengan pertanyaan
        filtered_data = filtered_data.loc[:, filtered_data.columns.str.contains(f"_{selected_pertanyaan}$")]

# Validasi data kosong
    if filtered_data.empty:
        st.warning("Tidak ada data yang sesuai dengan filter.")
    else:
        # Menghitung rata-rata per kategori dan pertanyaan
        kategori_data = filtered_data.columns.str.split('_').str[0]  # Ambil kategori dari nama kolom
        pertanyaan_data = filtered_data.columns.str.split('_').str[1]  # Ambil pertanyaan dari nama kolom
        kategori_data_full = []
        pertanyaan_data_full = []

        # Untuk setiap kolom, tetapkan kategori dan pertanyaan berdasarkan nama kolom
        for col in filtered_data.columns:
            kategori = col.split('_')[0]
            pertanyaan = col.split('_')[1]
            kategori_data_full.extend([kategori] * len(filtered_data))
            pertanyaan_data_full.extend([pertanyaan] * len(filtered_data))

        # Menyusun kategori_data_full dan pertanyaan_data_full ke dalam DataFrame yang memiliki jumlah baris yang sesuai
        filtered_data_long = pd.DataFrame(filtered_data.values.flatten(), columns=['nilai'])
        filtered_data_long['kategori'] = kategori_data_full
        filtered_data_long['pertanyaan'] = pertanyaan_data_full

        # Menghitung rata-rata skor per kategori dan pertanyaan
        avg_scores_df = calculate_avg_score(filtered_data_long, kategori_column='kategori', score_column='nilai', pertanyaan_column='pertanyaan')


    # Mengambil data tanpa mempertimbangkan filter yang diterapkan untuk pie chart (menggunakan data penuh)
    non_neutral_data_full = data[data.apply(lambda row: ~row.isin([]), axis=1)]  # Menghapus nilai netral (skor == 3)

    # Menghitung jumlah kategori berdasarkan data penuh
    categories_count_full = {
        "Sangat Kurang": (non_neutral_data_full == 1).sum().sum(),
        "Kurang": (non_neutral_data_full == 2).sum().sum(),
        "Baik": (non_neutral_data_full == 3).sum().sum(),
        "Sangat Baik": (non_neutral_data_full == 4).sum().sum(),
    }

    # Menghitung total jawaban non-netral pada data penuh
    total_non_neutral_full = sum(categories_count_full.values())

    # Menghitung persentase untuk setiap kategori
    fulfillment_data_full = pd.DataFrame({
        'Kategori': categories_count_full.keys(),
        'Jumlah': categories_count_full.values(),
        'Persentase': [count / total_non_neutral_full * 100 for count in categories_count_full.values()]
    })


    # Layout: Create three columns for the components
    col1, col2, col3 = st.columns([2, 4, 4])
    with col1:
        with st.container(border=True):
            # Membuat grafik donat dengan warna gradasi Purpor
            fig_donut = px.pie(
                fulfillment_data_full,
                values='Persentase',  # Data persentase
                names='Kategori',     # Nama kategori
                hole=0.4,             # Ukuran lubang tengah (donut)
                title=f"Persentase Terpenuhi dan Tidak Terpenuhi untuk Pertanyaan",
                color_discrete_sequence=px.colors.sequential.Purpor  # Warna gradasi Purpor
            )

            # Memperbarui tata letak grafik
            fig_donut.update_layout(
                title={
                    'text': "Distribusi Persentase Survey",
                    'y': 0.95,  # Posisi judul vertikal
                    'x': 0.5,   # Posisi judul horizontal (tengah)
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                legend_title="Indikator",       # Judul legenda
                legend_orientation="h",        # Orientasi legenda horizontal
                legend_yanchor="bottom",       # Penempatan legenda di bawah
                legend_y=-0.3,                 # Jarak vertikal legenda dari grafik
                legend_x=0.5,                  # Penempatan legenda di tengah horizontal
                legend_xanchor="center",       # Penempatan legenda sesuai pusat
                showlegend=True,   
                height=400,  # Height of the chart
                width=600  # Width of the chart            # Menampilkan legenda
            )

            # Menampilkan grafik donat di Streamlit
            st.plotly_chart(fig_donut, use_container_width=True)

        with col2:
            with st.container(border=True):
                # Menampilkan Bar Chart dengan grup berdasarkan kategori dan pertanyaan
                bar_chart = px.bar(
                    avg_scores_df,
                    x='kategori',  # Kategori pada sumbu X
                    y='nilai',  # Nilai rata-rata pada sumbu Y
                    color='pertanyaan',  # Kelompokkan berdasarkan pertanyaan
                    barmode='group',  # Group mode
                    title='Rata-rata Nilai per Kategori dan Pertanyaan',
                    labels={'nilai': 'Rata-Rata Nilai', 'kategori': 'Kategori', 'pertanyaan': 'Pertanyaan'},
                    height=450
                )
                # Update layout for the bar chart
                bar_chart.update_layout(
                    title_x=0.25,  # Position the title at the center
                    legend_title="Kategori",  # Title of the legend
                    legend_orientation="h",  # Horizontal legend
                    legend_yanchor="bottom",  # Position the legend at the bottom
                    legend_y=-0.3,  # Lower the legend
                    legend_x=0.5,  # Center the legend horizontally
                    legend_xanchor="center",  # Anchor the legend to the center
                    height=400,  # Height of the chart
                    width=600,  # Width of the chart
                )
                # Menghilangkan legend dengan update_layout
                bar_chart.update_layout(showlegend=False)
                
                # Menampilkan chart pada Streamlit
                st.plotly_chart(bar_chart, use_container_width=True)


    with col3:
        with st.container(border=True):
            ## Membuat bar chart horizontal dengan warna gradasi Purpor
            fig_bar_horizontal = px.bar(
                fulfillment_data_full,
                x='Persentase',  # Nilai persentase pada sumbu X
                y='Kategori',  # Kategori pada sumbu Y
                title="Distribusi Persentase Survey",
                color='Kategori',  # Memberikan warna berbeda untuk setiap kategori
                color_discrete_sequence=px.colors.sequential.Purpor,  # Warna gradasi Purpor
                orientation='h'  # Bar chart horizontal
            )

            # Update layout for the bar chart
            fig_bar_horizontal.update_layout(
                title_x=0.3,  # Center the title
                legend_title="Kategori",  # Title of the legend
                legend_orientation="h",  # Horizontal legend
                legend_yanchor="bottom",  # Position the legend at the bottom
                legend_y=-0.3,  # Lower the legend
                legend_x=0.5,  # Center the legend horizontally
                legend_xanchor="center",  # Anchor the legend to the center
                height=400,  # Height of the chart
                width=600,  # Width of the chart
            )

            # Menampilkan grafik horizontal bar di Streamlit
            st.plotly_chart(fig_bar_horizontal, use_container_width=True)

    # Menampilkan tabel rata-rata skor dengan kategori
    st.container(border=True)
    st.data_editor(
                avg_scores_df,
                column_config={
                    "nilai": st.column_config.ProgressColumn(
                        "nilai",
                        help="Menampilkan nilai rata-rata jawaban",
                        min_value=0,
                        max_value=5,  # Asumsikan skala 1-5
                        format="%.2f",  # Format nilai
                        ),
                    "Kategori": st.column_config.TextColumn(
                    "Kategori",
                    help="Kategori berdasarkan skor"
                    )
                    },
                    hide_index=True,
                    use_container_width=True
                )      

with tab2 :
    # Load data
    file_path = "C.4.KepuasanTendikterhadapSDM-prep.csv"  # Ganti dengan path ke file Anda
    data = load_data_with_multi_header(file_path)  # Memuat data dengan multi-header

            # Pisahkan kategori dan nilai dari kolom multi-header
    data_long = data.melt(var_name='kolom_asli', value_name='nilai')

    # Ekstraksi kategori dan pertanyaan dari nama kolom
    data_long['kategori'] = data_long['kolom_asli'].str.split('_').str[0]
    data_long['pertanyaan'] = data_long['kolom_asli'].str.split('_').str[1]

    # Drop kolom yang tidak diperlukan
    data_long = data_long.drop(columns=['kolom_asli'])

    # Menghitung rata-rata nilai per kategori
    avg_scores_permanent = calculate_avg_score_permanent(data_long, kategori_column='kategori', score_column='nilai')


    # Inisialisasi session_state untuk semua filter jika belum ada
    if 'selected_kategori' not in st.session_state:
        st.session_state['selected_kategori'] = 'All'
    if 'selected_pertanyaan' not in st.session_state:
        st.session_state['selected_pertanyaan'] = 'All'

    # FILTER 1: Kategori
    kategori_list = ['All'] + sorted(data.columns.str.split('_').str[0].unique())  # Ambil kategori dari level pertama
    selected_kategori = st.selectbox(
        '🔎Pilih Kategori :',
        options=kategori_list,
        index=kategori_list.index(st.session_state['selected_kategori']) if st.session_state['selected_kategori'] in kategori_list else 0
    )
    st.session_state['selected_kategori'] = selected_kategori

    # Filter data berdasarkan Kategori yang dipilih
    if selected_kategori == 'All':
        filtered_data = data
    else:
        # Pilih kolom yang sesuai dengan kategori
        filtered_data = data.loc[:, data.columns.str.startswith(selected_kategori)]

    # FILTER 2: Pertanyaan
    pertanyaan_list = ['All'] + sorted(filtered_data.columns.str.split('_').str[1].unique())  # Ambil pertanyaan dari level kedua
    selected_pertanyaan = st.selectbox(
        '🔎Pilih Pertanyaan :',
        options=pertanyaan_list,
        index=pertanyaan_list.index(st.session_state['selected_pertanyaan']) if st.session_state['selected_pertanyaan'] in pertanyaan_list else 0
    )
    st.session_state['selected_pertanyaan'] = selected_pertanyaan

    # Filter data berdasarkan Pertanyaan yang dipilih
    if selected_pertanyaan == 'All':
        filtered_data = filtered_data
    else:
        # Pilih kolom yang sesuai dengan pertanyaan
        filtered_data = filtered_data.loc[:, filtered_data.columns.str.contains(f"_{selected_pertanyaan}$")]

# Validasi data kosong
    if filtered_data.empty:
        st.warning("Tidak ada data yang sesuai dengan filter.")
    else:
        # Menghitung rata-rata per kategori dan pertanyaan
        kategori_data = filtered_data.columns.str.split('_').str[0]  # Ambil kategori dari nama kolom
        pertanyaan_data = filtered_data.columns.str.split('_').str[1]  # Ambil pertanyaan dari nama kolom
        kategori_data_full = []
        pertanyaan_data_full = []

        # Untuk setiap kolom, tetapkan kategori dan pertanyaan berdasarkan nama kolom
        for col in filtered_data.columns:
            kategori = col.split('_')[0]
            pertanyaan = col.split('_')[1]
            kategori_data_full.extend([kategori] * len(filtered_data))
            pertanyaan_data_full.extend([pertanyaan] * len(filtered_data))

        # Menyusun kategori_data_full dan pertanyaan_data_full ke dalam DataFrame yang memiliki jumlah baris yang sesuai
        filtered_data_long = pd.DataFrame(filtered_data.values.flatten(), columns=['nilai'])
        filtered_data_long['kategori'] = kategori_data_full
        filtered_data_long['pertanyaan'] = pertanyaan_data_full

        # Menghitung rata-rata skor per kategori dan pertanyaan
        avg_scores_df = calculate_avg_score(filtered_data_long, kategori_column='kategori', score_column='nilai', pertanyaan_column='pertanyaan')


    # Mengambil data tanpa mempertimbangkan filter yang diterapkan untuk pie chart (menggunakan data penuh)
    non_neutral_data_full = data[data.apply(lambda row: ~row.isin([]), axis=1)]  # Menghapus nilai netral (skor == 3)

    # Menghitung jumlah kategori berdasarkan data penuh
    categories_count_full = {
        "Sangat Kurang": (non_neutral_data_full == 1).sum().sum(),
        "Kurang": (non_neutral_data_full == 2).sum().sum(),
        "Baik": (non_neutral_data_full == 3).sum().sum(),
        "Sangat Baik": (non_neutral_data_full == 4).sum().sum(),
    }

    # Menghitung total jawaban non-netral pada data penuh
    total_non_neutral_full = sum(categories_count_full.values())

    # Menghitung persentase untuk setiap kategori
    fulfillment_data_full = pd.DataFrame({
        'Kategori': categories_count_full.keys(),
        'Jumlah': categories_count_full.values(),
        'Persentase': [count / total_non_neutral_full * 100 for count in categories_count_full.values()]
    })


    # Layout: Create three columns for the components
    col1, col2, col3 = st.columns([2, 4, 4])
    with col1:
        with st.container(border=True):
            # Membuat grafik donat dengan warna gradasi Purpor
            fig_donut = px.pie(
                fulfillment_data_full,
                values='Persentase',  # Data persentase
                names='Kategori',     # Nama kategori
                hole=0.4,             # Ukuran lubang tengah (donut)
                title=f"Persentase Terpenuhi dan Tidak Terpenuhi untuk Pertanyaan",
                color_discrete_sequence=px.colors.sequential.Purpor  # Warna gradasi Purpor
            )

            # Memperbarui tata letak grafik
            fig_donut.update_layout(
                title={
                    'text': "Distribusi Persentase Survey",
                    'y': 0.95,  # Posisi judul vertikal
                    'x': 0.5,   # Posisi judul horizontal (tengah)
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                legend_title="Indikator",       # Judul legenda
                legend_orientation="h",        # Orientasi legenda horizontal
                legend_yanchor="bottom",       # Penempatan legenda di bawah
                legend_y=-0.3,                 # Jarak vertikal legenda dari grafik
                legend_x=0.5,                  # Penempatan legenda di tengah horizontal
                legend_xanchor="center",       # Penempatan legenda sesuai pusat
                showlegend=True,   
                height=400,  # Height of the chart
                width=600  # Width of the chart            # Menampilkan legenda
            )

            # Menampilkan grafik donat di Streamlit
            st.plotly_chart(fig_donut, use_container_width=True)

        with col2:
            with st.container(border=True):
                # Menampilkan Bar Chart dengan grup berdasarkan kategori dan pertanyaan
                bar_chart = px.bar(
                    avg_scores_df,
                    x='kategori',  # Kategori pada sumbu X
                    y='nilai',  # Nilai rata-rata pada sumbu Y
                    color='pertanyaan',  # Kelompokkan berdasarkan pertanyaan
                    barmode='group',  # Group mode
                    title='Rata-rata Nilai per Kategori dan Pertanyaan',
                    labels={'nilai': 'Rata-Rata Nilai', 'kategori': 'Kategori', 'pertanyaan': 'Pertanyaan'},
                    height=450
                )
                # Update layout for the bar chart
                bar_chart.update_layout(
                    title_x=0.25,  # Position the title at the center
                    legend_title="Kategori",  # Title of the legend
                    legend_orientation="h",  # Horizontal legend
                    legend_yanchor="bottom",  # Position the legend at the bottom
                    legend_y=-0.3,  # Lower the legend
                    legend_x=0.5,  # Center the legend horizontally
                    legend_xanchor="center",  # Anchor the legend to the center
                    height=400,  # Height of the chart
                    width=600,  # Width of the chart
                )
                # Menghilangkan legend dengan update_layout
                bar_chart.update_layout(showlegend=False)
                
                # Menampilkan chart pada Streamlit
                st.plotly_chart(bar_chart, use_container_width=True)


    with col3:
        with st.container(border=True):
            ## Membuat bar chart horizontal dengan warna gradasi Purpor
            fig_bar_horizontal = px.bar(
                fulfillment_data_full,
                x='Persentase',  # Nilai persentase pada sumbu X
                y='Kategori',  # Kategori pada sumbu Y
                title="Distribusi Persentase Survey",
                color='Kategori',  # Memberikan warna berbeda untuk setiap kategori
                color_discrete_sequence=px.colors.sequential.Purpor,  # Warna gradasi Purpor
                orientation='h'  # Bar chart horizontal
            )

            # Update layout for the bar chart
            fig_bar_horizontal.update_layout(
                title_x=0.3,  # Center the title
                legend_title="Kategori",  # Title of the legend
                legend_orientation="h",  # Horizontal legend
                legend_yanchor="bottom",  # Position the legend at the bottom
                legend_y=-0.3,  # Lower the legend
                legend_x=0.5,  # Center the legend horizontally
                legend_xanchor="center",  # Anchor the legend to the center
                height=400,  # Height of the chart
                width=600,  # Width of the chart
            )

            # Menampilkan grafik horizontal bar di Streamlit
            st.plotly_chart(fig_bar_horizontal, use_container_width=True)

    # Menampilkan tabel rata-rata skor dengan kategori
    st.container(border=True)
    st.data_editor(
                avg_scores_df,
                column_config={
                    "nilai": st.column_config.ProgressColumn(
                        "nilai",
                        help="Menampilkan nilai rata-rata jawaban",
                        min_value=0,
                        max_value=5,  # Asumsikan skala 1-5
                        format="%.2f",  # Format nilai
                        ),
                    "Kategori": st.column_config.TextColumn(
                    "Kategori",
                    help="Kategori berdasarkan skor"
                    )
                    },
                    hide_index=True,
                    use_container_width=True
                )      
