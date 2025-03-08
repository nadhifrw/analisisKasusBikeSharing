import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Mengatur konfigurasi halaman
st.set_page_config(
    page_title="Bike Sharing Analysis",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    day_df = pd.read_csv('data/data-1.csv')
    hour_df = pd.read_csv('data/data-2.csv')
    
    # Mengubah kolom tanggal ke datetime
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    # Membuat kolom datetime dengan menggabungkan tanggal dan jam
    hour_df['datetime'] = pd.to_datetime(hour_df['dteday'].dt.strftime('%Y-%m-%d') + ' ' + 
                                         hour_df['hr'].astype(str).str.zfill(2) + ':00:00')
    
    # Mengubahkah musim, tahun, bulan, hari libur, hari kerja, hari libur, hari kerja, kolom ke tipe data kategorikal
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    yr_map = {0: '2011', 1: '2012'}
    month_map = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 
                6: 'June', 7: 'July', 8: 'August', 9: 'September', 
                10: 'October', 11: 'November', 12: 'December'}
    weekday_map = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 
                4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
    holiday_map = {0: 'No Holiday', 1: 'Holiday'}
    workingday_map = {0: 'Non-working day', 1: 'Working day'}
    weather_map = {
        1: 'Clear (Clear, Few clouds, Partly cloudy)',
        2: 'Mist (Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist)',
        3: 'Light Precipitation (Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds)',
        4: 'Heavy Precipitation (Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog)'
    }

    # Mengaplikasukan mapping 
    day_df['season'] = day_df['season'].map(season_map)
    day_df['yr'] = day_df['yr'].map(yr_map)
    day_df['mnth'] = day_df['mnth'].map(month_map)
    day_df['weekday'] = day_df['weekday'].map(weekday_map)
    day_df['holiday'] = day_df['holiday'].map(holiday_map)
    day_df['workingday'] = day_df['workingday'].map(workingday_map)
    day_df['weathersit'] = day_df['weathersit'].map(weather_map)
    hour_df['season'] = hour_df['season'].map(season_map)
    hour_df['yr'] = hour_df['yr'].map(yr_map)
    hour_df['mnth'] = hour_df['mnth'].map(month_map)
    hour_df['weekday'] = hour_df['weekday'].map(weekday_map)
    hour_df['holiday'] = hour_df['holiday'].map(holiday_map)
    hour_df['workingday'] = hour_df['workingday'].map(workingday_map)
    hour_df['weathersit'] = hour_df['weathersit'].map(weather_map)

    # Membuat suhu, kelembaban, dan kecepatan angin yang dinormalisasi untuk visualisasi yang lebih baik
    day_df['normalized_temp'] = day_df['temp'] * 41  # According to documentation
    hour_df['normalized_temp'] = hour_df['temp'] * 41
    
    return day_df, hour_df

# Header utama
st.markdown("<h1 class='main-header'>Bike Sharing Analysis Dashboard</h1>", unsafe_allow_html=True)

# Memuat data
try:
    day_df, hour_df = load_data()
    st.success("Data loaded successfully!")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar untuk pemfilteran
st.sidebar.header("Filters")

# Filter tanggal
min_date = day_df['dteday'].min().date()
max_date = day_df['dteday'].max().date()
start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)
st.sidebar.markdown("<h4>Pilih tanggal yang ada di atas untuk menentukan batas awal dan akhir yang ditampilkan</h4>", unsafe_allow_html=True)
st.sidebar.markdown(f"<h4>Data yang ditunjukan {start_date} to {end_date} </h4>", unsafe_allow_html=True)
# Menampilkan tab utama
tab1, tab2, tab3, tab4, = st.tabs([
    "☁️ Weather Impact", 
    "📅 Holiday Analysis", 
    "🌞 Seasonal Patterns", 
    "🕒 Hourly Trends"
])

# Tab 1: Analisis Dampak Cuaca
with tab1:
    st.markdown("<h2 class='section-header'>Weather Impact on Bike Rentals</h2>", unsafe_allow_html=True)
    
    # Grouping untuk kondisi cuaca dan jumlah sewa
    rentals_by_weather = day_df.groupby('weathersit')['cnt'].sum()

    # Menghitung persentase
    percentage_by_weather = (rentals_by_weather / rentals_by_weather.sum()) * 100

    # Menvisualisasikan menggunakan pie chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(percentage_by_weather, autopct='%1.2f%%', startangle=90)
    ax.set_title('Percentage of Bike Rentals by Weather Condition')
    ax.axis('equal')  
    ax.legend(percentage_by_weather.index, loc="best")
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("<div class='insight-box'>", unsafe_allow_html=True)
    st.markdown("""
    ### **Insight:**
                
    - **68.57% perentalan terjadi ketika cuaca yang cerah** 
    - **30.27% perentalan terjadi ketika cuaca Cloudy (Berawan)** 
    - **1.15% perentalan terjadi ketika cuaca Light Percipatation (light rain/snow)**
    - **Tidak ada perentalan terjadi ketika cuaca Heavy Percipatation (heavy rain/snow)**
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Tab 2: Holiday & Weekend Impact Analysis
with tab2:
    st.markdown("<h2 class='section-header'>Holiday & Weekend Impact Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        workingday_comparison = day_df.groupby('workingday')[['casual', 'registered', 'cnt']].mean().reset_index()

        fig, ax = plt.subplots(figsize=(10, 6))
        workingday_melted = pd.melt(workingday_comparison, id_vars=['workingday'],
                                value_vars=['casual', 'registered'],
                                var_name='User Type', value_name='Average Rentals')

        sns.barplot(x='workingday', y='Average Rentals', hue='User Type', data=workingday_melted, ax=ax)
        ax.set_xlabel('Day Type')
        ax.set_ylabel('Average Rentals')
        ax.set_title('Average Rentals on Working Days vs. Non-Working Days')
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Dampak hari libur
        holiday_comparison = day_df.groupby('holiday')[['casual', 'registered', 'cnt']].mean().reset_index()

        fig, ax = plt.subplots(figsize=(10, 6))
        holiday_melted = pd.melt(holiday_comparison, id_vars=['holiday'], 
                                value_vars=['casual', 'registered'], 
                                var_name='User Type', value_name='Average Rentals')

        sns.barplot(x='holiday', y='Average Rentals', hue='User Type', data=holiday_melted, ax=ax)
        ax.set_xlabel('Day Type')
        ax.set_ylabel('Average Rentals')
        ax.set_title('Average Rentals on Holidays vs. Regular Days')
        plt.tight_layout()
        st.pyplot(fig)
    
    # Analisis hari kerja
    st.markdown("<h3 class='subsection-header'>Rentals by Day of Week</h3>", unsafe_allow_html=True)
    
    weekday_analysis = day_df.groupby('weekday')[['casual', 'registered', 'cnt']].mean().reset_index()

    # Menentukan urutan kustom untuk hari dalam seminggu dimulai dari Senin
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Mengurutkan ulang DataFrame menggunakan tipe data kategorikal
    weekday_analysis['weekday'] = pd.Categorical(weekday_analysis['weekday'], categories=weekday_order, ordered=True)
    weekday_analysis = weekday_analysis.sort_values('weekday')

    fig, ax = plt.subplots(figsize=(12, 6))
    width = 0.35
    x = np.arange(len(weekday_analysis))

    casual = ax.bar(x - width/2, weekday_analysis['casual'], width, label='Casual')
    registered = ax.bar(x + width/2, weekday_analysis['registered'], width, label='Registered')

    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Average Rentals')
    ax.set_title('Average Bike Rentals by Day of Week')
    ax.set_xticks(x)
    ax.set_xticklabels(weekday_analysis['weekday'])
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown("<div class='insight-box'>", unsafe_allow_html=True)
    st.markdown("""
    ### **Insight:**
    - **Perentalan paling sering terjadi pada working day dengan registered sebagai perental terbesar**
    - **Terjadi sedikit penurunan pada weekend pada kategori registered**
    - **Terjadi peningkatan pada weekend pada kategori casual**
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Tab 3: Seasonal Analysis
with tab3:
    st.markdown("<h2 class='section-header'>Seasonal Analysis</h2>", unsafe_allow_html=True)
    
    # Analisis gabungan musim dan cuaca
    st.markdown("<h3 class='subsection-header'>Season and Weather Combined Impact</h3>", unsafe_allow_html=True)

    # Grouping berdasarkan musim dan menghitung beberapa statistik
    rental_by_season_type = day_df.groupby('season').agg({
        'cnt': ['sum', 'mean', 'count'],
        'casual': ['sum', 'mean', 'count'],
        'registered': ['sum', 'mean', 'count'],
    }).reset_index().sort_values(by=('cnt', 'sum'), ascending=False)

    # Mengatur ukuran figure dan create figure object
    fig, ax = plt.subplots(figsize=(12, 6))

    # Menyiapkan data untuk plotting
    seasons = rental_by_season_type['season']
    total_rentals = rental_by_season_type[('cnt', 'sum')]
    casual_rentals = rental_by_season_type[('casual', 'sum')]
    registered_rentals = rental_by_season_type[('registered', 'sum')]

    # Mebuat chart dengan semua data dijadikan satu plot
    x = range(len(seasons))
    width = 0.25

    ax.bar([i - width for i in x], total_rentals, width=width, label='Total Rentals')
    ax.bar([i for i in x], casual_rentals, width=width, label='Casual Rentals')
    ax.bar([i + width for i in x], registered_rentals, width=width, label='Registered Rentals')

    # Menambahkan title dan label
    ax.set_xlabel('Season')
    ax.set_ylabel('Number of Rentals')
    ax.set_title('Bike Rentals by Season')
    ax.set_xticks(x)
    ax.set_xticklabels(seasons)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Menampilkan plot dengan tight layout
    plt.tight_layout()
    st.pyplot(fig)  
    
    st.markdown("<div class='insight-box'>", unsafe_allow_html=True)
    st.markdown("""
    ### **Insight:**
    - **Musim gugur menunjukan perental terbanyak pada kategori casual maupun registered**
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Tab 4: Hourly Rental Patterns
with tab4:
    st.markdown("<h2 class='section-header'>Hourly Rental Patterns</h2>", unsafe_allow_html=True)
    
    # Pola per jam secara keseluruhan
    st.markdown("<h3 class='subsection-header'>Total Rentals by Hour</h3>", unsafe_allow_html=True)

    # Grouping berdasarkan jam
    hourly_stats = hour_df.groupby('hr').agg({
        'cnt': 'sum', 
        'casual':['sum' ,'mean'], 
        'registered': ['sum' ,'mean'],
    }).sort_values(by=('cnt', 'sum'), ascending=False)

    # Membuat kategori waktu
    conditions = [
        (hour_df['hr'] >= 22) | (hour_df['hr'] < 5),  # Malam (10 PM - 5 AM) (22 - 5)
        (hour_df['hr'] >= 5) & (hour_df['hr'] < 11),   # Pagi (5 AM - 11 AM) (5 - 11)
        (hour_df['hr'] >= 11) & (hour_df['hr'] < 15),  # Siang (11 AM - 3 PM) (11 - 15)
        (hour_df['hr'] >= 15) & (hour_df['hr'] < 22)   # Sore (3 PM - 10 PM) (15 - 22)
    ]

    # Mendifinisikan kategori waktu
    choices = ['Malam', 'Pagi', 'Siang', 'Sore']

    # Membuat kolom baru dengan kategori waktu
    hour_df['time_of_day'] = np.select(conditions, choices, default='Unknown')

    time_analysis = hour_df.groupby('time_of_day').agg({
        'cnt': ['mean', 'count', 'sum']
    }).reset_index()
    
    # Mereset index untuk membuat 'hr' menjadi kolom
    hourly_stats = hourly_stats.reset_index()

    # Mengurutkan berdasarkan jam untuk visualisasi timeline 
    hourly_stats = hourly_stats.sort_values(by='hr')

    # Plot 1: Distribusi Per Jam
    fig1, ax1 = plt.subplots(figsize=(12, 6))

    # Plot menggunakan total rental, casual, dan registered berdasarkan jamnya
    ax1.plot(hourly_stats['hr'], hourly_stats[('cnt', 'sum')], marker='o', linewidth=2, label='Total Rides')
    ax1.plot(hourly_stats['hr'], hourly_stats[('casual', 'sum')], marker='s', linewidth=2, label='Casual Rides')
    ax1.plot(hourly_stats['hr'], hourly_stats[('registered', 'sum')], marker='^', linewidth=2, label='Registered Rides')

    # Menambahkan label dan judul
    ax1.set_xlabel('Hour of Day')
    ax1.set_ylabel('Number of Rides')
    ax1.set_title('Bike Rentals by Hour of Day')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.set_xticks(range(0, 24))
    ax1.legend()

    # Menampilkan plot
    plt.tight_layout()
    st.pyplot(fig1)

    # Pola per jam secara keseluruhan
    st.markdown("<h3 class='subsection-header'>Total Rentals by Time of Days</h3>", unsafe_allow_html=True)

    # Plot 2: Analisis Waktu Hari
    fig2, ax2 = plt.subplots(figsize=(12, 6))

    # Memasukan data untuk plotting
    seasons = time_analysis['time_of_day']
    total_rentals = time_analysis[('cnt', 'sum')]

    # Membuat X untuk posisi bar
    x = range(len(seasons))
    width = 0.7

    ax2.bar(x, total_rentals, width=width, label='Total Rentals')

    # Menambahkan label dan judul
    ax2.set_xlabel('Time of Day')
    ax2.set_ylabel('Number of Rentals')
    ax2.set_title('Bike Rentals by Time of Day')
    ax2.set_xticks(x)
    ax2.set_xticklabels(seasons)
    ax2.legend()
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    # Menampilkan plot
    plt.tight_layout()
    st.pyplot(fig2)
    
    st.markdown("<div class='insight-box'>", unsafe_allow_html=True)
    st.markdown("""
    ### **Insight:**
    - **Pengguna casual mulai meningkat sekitar jam 9 pagi**
    - **Puncak penggunaan ditunjukan pada jam 8 pagi (8 AM) dan juga 3 sore (17 PM)**
    - **Perentalan paling sering terjadi pada range jam sore (3 PM - 10 PM) (15 - 22), diikuti dengan range jam pagi (5 AM - 11 AM) (5 - 11)**
    """)
    st.markdown("</div>", unsafe_allow_html=True)
