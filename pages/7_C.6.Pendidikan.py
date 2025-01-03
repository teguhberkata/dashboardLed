import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="📊Survey Evaluasi Tingkat Kepuasan Dosen Dan Tenaga Kependidikan Terhadap Sistem Pengelolaan SDM",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Menampilkan judul aplikasi di tengah
st.markdown("""
    <h2 style="text-align: center;">Survey Kepuasan Pembelajaran (SIMAK)</h2>
""", unsafe_allow_html=True)


# Fungsi untuk memuat data dengan caching
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# Fungsi untuk membersihkan data
def clean_data(data, start_col=1):
    for col in data.columns[start_col:]:
        data[col] = data[col].astype(str).str.extract(r'(\d+)').astype(float)
    return data


# Fungsi untuk menghitung rata-rata per kompetensi
def calculate_avg_score(data, kompetensi_column='Kompetensi', score_column='Rata-rata per Kompetensi'):
    return data.groupby(kompetensi_column)[score_column].mean()


# Menambahkan kolom kategori berdasarkan nilai skor
def determine_category(score):
    if score < 1.0:
        return "Sangat Kurang"
    elif score < 2.0:
        return "Kurang"
    elif score < 3.0:
        return "Netral"
    elif score < 4.0:
        return "Baik"
    else:
        return "Sangat Baik"

# Tampilkan deskripsi survei dan grafik
tab1, tab2 = st.tabs(["Survey Kepuasan Dosen", "Survey Kepuasan Tenaga Pendidik"])

with tab1:

    # Load data
    data = load_data("C.6.Kepuasandosen-prep.csv")

    # Inisialisasi session_state untuk semua filter jika belum ada
    if 'selected_tahun' not in st.session_state:
        st.session_state['selected_tahun'] = 'All'
    if 'selected_dosen' not in st.session_state:
        st.session_state['selected_dosen'] = 'All'
    if 'selected_matakuliah' not in st.session_state:
        st.session_state['selected_matakuliah'] = 'All'

    # FILTER 1: Tahun Akademik
    tahun_akademik_list = ['All'] + sorted(data['Tahun Akademik'].unique())
    selected_tahun = st.selectbox(
        '🔎Pilih Tahun Akademik :',
        options=tahun_akademik_list,
        index=tahun_akademik_list.index(st.session_state['selected_tahun']) if st.session_state['selected_tahun'] in tahun_akademik_list else 0
    )
    st.session_state['selected_tahun'] = selected_tahun

    # Filter data berdasarkan Tahun Akademik
    filtered_data = data if selected_tahun == 'All' else data[data['Tahun Akademik'] == selected_tahun]

    # FILTER 2: Nama Dosen
    dosen_list = ['All'] + sorted(filtered_data['Nama Dosen'].unique())
    selected_dosen = st.selectbox(
        '🔎Pilih Nama Dosen :',
        options=dosen_list,
        index=dosen_list.index(st.session_state['selected_dosen']) if st.session_state['selected_dosen'] in dosen_list else 0
    )
    st.session_state['selected_dosen'] = selected_dosen

    # Filter data berdasarkan Nama Dosen
    filtered_data = filtered_data if selected_dosen == 'All' else filtered_data[filtered_data['Nama Dosen'] == selected_dosen]

    # FILTER 3: Mata Kuliah
    matakuliah_list = ['All'] + sorted(filtered_data['Matakuliah'].unique())
    selected_matakuliah = st.selectbox(
        '🔎Pilih Mata Kuliah :',
        options=matakuliah_list,
        index=matakuliah_list.index(st.session_state['selected_matakuliah']) if st.session_state['selected_matakuliah'] in matakuliah_list else 0
    )
    st.session_state['selected_matakuliah'] = selected_matakuliah

    # Filter data berdasarkan Mata Kuliah
    filtered_data = filtered_data if selected_matakuliah == 'All' else filtered_data[filtered_data['Matakuliah'] == selected_matakuliah]

    # Validasi data kosong
    if filtered_data.empty:
        st.warning("Tidak ada data yang sesuai dengan filter.")
    else:
       # Menghitung rata-rata per kompetensi
        avg_scores_df = calculate_avg_score(filtered_data)

        # Cek apakah ada kompetensi yang tersedia dalam data yang sudah difilter
        kompetensi_list = ['Pedagogik', 'Profesional', 'Kepribadian', 'Sosial']
        available_kompetensi = [kompetensi for kompetensi in kompetensi_list if kompetensi in filtered_data['Kompetensi'].unique()]

        if not available_kompetensi:
            st.warning("Tidak ada kompetensi yang tersedia setelah penerapan filter.")
        else:
            # Membuat layout dengan 4 kolom untuk menampilkan pie chart
            cols = st.columns(4)

            # Menampilkan Pie Chart untuk setiap kompetensi yang tersedia
            for i, kompetensi in enumerate(available_kompetensi):
                # Filter data untuk kompetensi tertentu
                kompetensi_data = filtered_data[filtered_data['Kompetensi'] == kompetensi]
                
                # Menghitung rata-rata skor untuk kompetensi ini
                avg_score = kompetensi_data['Rata-rata per Kompetensi'].mean()
                fulfilled_percentage = (avg_score / 5) * 100
                not_fulfilled_percentage = 100 - fulfilled_percentage

                # Persiapkan data untuk donut chart
                fulfillment_data = pd.DataFrame({
                    'Status': ['Puas', 'Tidak Puas'],
                    'Persentase': [fulfilled_percentage, not_fulfilled_percentage]
                })

                # Membuat container dengan border untuk setiap pie chart
                with cols[i]:
                    with st.container(border=True):
                        
                        fig_donut = px.pie(
                            fulfillment_data,
                            values='Persentase',
                            names='Status',
                            hole=0.4,
                            title=f"Persentase Kompetensi {kompetensi}",
                            color_discrete_sequence=px.colors.sequential.Purpor
                        )

                        # Update layout untuk menyesuaikan tampilan
                        fig_donut.update_layout(
                            title_x=0.15,  # Centers the title
                            legend_title="Indikator",  # Title for the legend
                            legend_orientation="h",  # Horizontal legend
                            legend_yanchor="middle",  # Aligns legend in the middle
                            legend_y=-0.3,  # Moves the legend below the chart
                            legend_x=0.5,  # Centers the legend horizontally
                            legend_xanchor="center",  # Ensures that the legend is anchored in the center
                            height=300,  # Reduce height
                            width=200   # Reduce width
                        )

                        # Display the donut chart in the corresponding container
                        st.plotly_chart(fig_donut, use_container_width=True)


        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                # Menggabungkan seluruh data kompetensi menjadi satu distribusi
                # Menghitung distribusi nilai untuk seluruh data kompetensi
                categories_count_all = {
                    "Sangat Kurang": (data['Rata-rata per Kompetensi'] == 1).sum(),
                    "Kurang": (data['Rata-rata per Kompetensi'] == 2).sum(),
                    "Baik": (data['Rata-rata per Kompetensi'] == 4).sum(),
                    "Sangat Baik": (data['Rata-rata per Kompetensi'] == 5).sum(),
                }

                # Hitung total jawaban yang relevan
                total_non_neutral_all = sum(categories_count_all.values())

                # Hitung persentase untuk setiap kategori
                fulfillment_data_all = pd.DataFrame({
                    'Kategori': categories_count_all.keys(),
                    'Jumlah': categories_count_all.values(),
                    'Persentase': [count / total_non_neutral_all * 100 for count in categories_count_all.values()]
                })

                # Buat diagram pie untuk distribusi seluruh kompetensi
                fig_donut_all = px.pie(
                    fulfillment_data_all,
                    values='Persentase',
                    names='Kategori',
                    hole=0.4,
                    title="Distribusi Kategori Jawaban (Seluruh Kompetensi)",
                    color_discrete_sequence=px.colors.sequential.Purpor
                )

                # Update layout untuk menyesuaikan tampilan
                fig_donut_all.update_layout(
                    title_x=0.25,  # Centers the title
                    legend_title="Kategori",  # Title for the legend
                    legend_orientation="h",  # Horizontal legend
                    legend_yanchor="bottom",  # Aligns legend at the bottom
                    legend_y=-0.2,  # Moves the legend below the chart
                    legend_x=0.5,  # Centers the legend horizontally
                    legend_xanchor="center"  # Ensures that the legend is anchored in the center
                )

                # Menampilkan diagram pie untuk seluruh kompetensi
                st.plotly_chart(fig_donut_all, use_container_width=True)

                        
        with col2:
            with st.container(border=True):
                barchart = px.bar(
                    filtered_data,
                    x='Rata-rata per Kompetensi',
                    y='Tahun Akademik',
                    color='Kompetensi',
                    barmode='group',
                    title='Rata-rata Nilai Kompetensi per Tahun Akademik',
                    labels={
                        'Rata-rata per Kompetensi': 'Rata-rata Nilai',
                        'Tahun Akademik': 'Tahun Akademik',
                        'Kompetensi': 'Kompetensi'
                    },
                    height=450
                )
                st.plotly_chart(barchart)

    # Tampilkan tabel dengan kolom Progress (Rata-rata per Kompetensi)
        st.data_editor(
                filtered_data[['Tahun Akademik', 'Nama Dosen', 'Matakuliah', 'Kompetensi', 'Rata-rata per Kompetensi', 'Kategori per Kompetensi']],
                column_config={
                    "Rata-rata per Kompetensi": st.column_config.ProgressColumn(
                        "Rata-rata per Kompetensi",
                        help="Menampilkan nilai rata-rata kompetensi",
                        min_value=0,
                        max_value=5,  # Sesuaikan dengan rentang nilai kompetensi
                        format="%.2f",  # Format nilai
                    ),
                },
                hide_index=True,
               use_container_width=True  
            )
  # Tab 3: SARANA TENDIK
with tab2:
    # Load data
    data1 = load_data("C.6.Kepuasantendik-prep.csv")

    # Calculate average scores for each question
    avg_scores = data1.mean()

    # Prepare the indicator names (letters for X-axis)
    questions = data1.columns.tolist()  # Assuming questions are column names
    letters = [chr(i) for i in range(97, 97 + len(avg_scores))]  # ['a', 'b', 'c', ...]

    # Create a DataFrame with letters as 'Indikator', average scores, and questions
    avg_scores_df = pd.DataFrame({
        'Indikator': letters,
        'Pertanyaan': questions,
        'Rata-Rata Skor': avg_scores.values
    })

    
    # Terapkan fungsi kategori ke setiap nilai skor rata-rata
    avg_scores_df['Kategori'] = avg_scores_df['Rata-Rata Skor'].apply(determine_category)

        # Tambahkan opsi "All" di awal daftar pertanyaan
    all_questions = ["All"] + questions

    # Perbarui selectbox untuk menyertakan opsi "All"
    selected_question_index = st.selectbox(
        "🔎 Pilih Pertanyaan :",
        range(len(all_questions)),
        format_func=lambda x: all_questions[x]
    )

    # Jika "All" dipilih, hitung data gabungan, jika tidak, ambil pertanyaan spesifik
    if selected_question_index == 0:  # "All" dipilih
        selected_question_avg_score = avg_scores_df['Rata-Rata Skor'].mean()
        fulfilled_percentage = (selected_question_avg_score / 5) * 100
        not_fulfilled_percentage = 100 - fulfilled_percentage
    else:
        selected_question_avg_score = avg_scores_df['Rata-Rata Skor'].iloc[selected_question_index - 1]
        fulfilled_percentage = (selected_question_avg_score / 5) * 100
        not_fulfilled_percentage = 100 - fulfilled_percentage

    # Persiapkan data untuk donut chart
    fulfillment_data = pd.DataFrame({
        'Status': ['Puas', 'Tidak Puas'],
        'Persentase': [fulfilled_percentage, not_fulfilled_percentage]
    })

        # Filter data tanpa netral (skor == 3 dianggap netral)
    non_neutral_data = data1[data1.apply(lambda row: ~row.isin([3]), axis=1)]

    # Hitung jumlah kategori
    categories_count = {
        "Sangat Kurang": (non_neutral_data == 1).sum().sum(),
        "Kurang": (non_neutral_data == 2).sum().sum(),
        "Baik": (non_neutral_data == 4).sum().sum(),
        "Sangat Baik": (non_neutral_data == 5).sum().sum(),
    }

    # Hitung total jawaban yang relevan
    total_non_neutral = sum(categories_count.values())

    # Hitung persentase untuk setiap kategori
    fulfillment_data1 = pd.DataFrame({
        'Kategori': categories_count.keys(),
        'Jumlah': categories_count.values(),
        'Persentase': [count / total_non_neutral * 100 for count in categories_count.values()]
    })

            # Create the fulfillment_data DataFrame
    fulfillment_data = pd.DataFrame({
        'Status': ['Puas', 'Tidak Puas'],  # Change 'Kategori' to 'Status'
        'Persentase': [fulfilled_percentage, not_fulfilled_percentage]
    })

    col1, col2 = st.columns(2)

    with col1:
        
        with st.container(border=True): 
            # Create the donut chart
            fig_donut = px.pie(
                fulfillment_data,
                values='Persentase',
                names='Status',
                hole=0.4,
                title=f"Persentase Puas dan Tidak Puas untuk Pertanyaan",
                color_discrete_sequence=px.colors.sequential.Purpor
            )
            # Update layout to center the title and position the legend at the bottom
            fig_donut.update_layout(
                title_x=0.2,  # Centers the title
                legend_title="Indikator",  # Title for the legend
                legend_orientation="h",  # Horizontal legend
                legend_yanchor="bottom",  # Aligns legend at the bottom
                legend_y=-0.5,  # Moves the legend below the chart
                legend_x=0.5,  # Centers the legend horizontally
                legend_xanchor="center"  # Ensures that the legend is anchored in the center
            )
            # Display the donut chart
            st.plotly_chart(fig_donut,use_container_width=True)

 
        
        with st.container(border=True):    # Line Chart for the average scores of each indicator

            fig_line = px.line(
                avg_scores_df,
                x='Indikator',
                y='Rata-Rata Skor',
                labels={'Indikator': 'Indikator', 'Rata-Rata Skor': 'Rata-Rata Skor'},
                title="Perubahan Skor Rata-Rata untuk Setiap Indikator",
                markers=True,
                height=400,
            )

            # Update the line color to use the Purpor color scale
            fig_line.update_traces(
                line=dict(color='rgba(255, 99, 71, 1)'),  # Default line color if you want specific color
                marker=dict(color=avg_scores_df['Rata-Rata Skor'], colorscale='Purpor')  # Applying color scale to markers
            )

            # Update layout for line chart
            fig_line.update_layout(
                title_x=0.2,  # Centers the title
                title_y=0.95,  # Adjusts the title position vertically
                title_font=dict(size=20, color="white"),  # Title font size and color
                xaxis_title="Indikator",
                yaxis_title="Rata-Rata Skor",
                xaxis=dict(
                    tickmode='array', 
                    tickvals=avg_scores_df['Indikator'],  # Use the actual indicator names for ticks
                    showgrid=True,
                    gridcolor='#cecdcd',  # Light grid color for x-axis
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#cecdcd',  # Light grid color for y-axis
                ),
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent plot background
                paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent paper background
                font=dict(color='#cecdcd'),  # Font color for the chart
            )

            # Display the line chart
            st.plotly_chart(fig_line,use_container_width=True)

    with col2:
        with st.container(border=True):
            # Donut chart with the correct names column
            fig_donut = px.pie(
                fulfillment_data1,
                values='Persentase',
                names='Kategori',  # This should be 'Kategori' as defined in the DataFrame
                hole=0.4,
                title="Distribusi Kategori Jawaban",
                color_discrete_sequence=px.colors.sequential.Purp
            )

            # Update layout for better visualization
            fig_donut.update_layout(
                title_x=0.35,
                legend_title="Kategori",
                legend_orientation="h",
                legend_yanchor="bottom",
                legend_y=-0.2,
                legend_x=0.5,
                legend_xanchor="center"
            )

            # Display the donut chart
            st.plotly_chart(fig_donut, use_container_width=True)
        

        with st.container(border=True):
            # Plot a bar chart for average scores
            fig_bar = px.bar(
                avg_scores_df,
                x='Indikator',
                y='Rata-Rata Skor',
                labels={'Indikator': 'Indikator', 'Rata-Rata Skor': 'Rata-Rata Skor'},
                title="Rata-Rata Skor untuk Setiap Indikator",
                color='Rata-Rata Skor',
                color_continuous_scale='Purpor',
                height=400,
                hover_data=["Rata-Rata Skor"]
            )

            fig_bar.update_layout(
                title_x=0.2
            )

            st.plotly_chart(fig_bar,use_container_width=True)

    # Display data editor with category column
    st.container(border=True)
    st.data_editor(
        avg_scores_df,
        column_config={
            "Rata-Rata Skor": st.column_config.ProgressColumn(
                "Rata-rata Skor",
                help="Menampilkan nilai rata-rata jawaban",
                min_value=0,
                max_value=5,
                format="%.2f",
            ),
            "Kategori": st.column_config.TextColumn(
                "Kategori",
                help="Kategori berdasarkan skor"
            )
        },
        hide_index=True,
        use_container_width=True
    )
