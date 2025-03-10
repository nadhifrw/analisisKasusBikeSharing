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

# Fix 1: Correct data loading path
@st.cache_data
def load_data():
    try:
        # First try with data/ prefix (project root)
        day_df = pd.read_csv('data/data-1.csv')
        hour_df = pd.read_csv('data/data-2.csv')
    except FileNotFoundError:
        # Fallback to local directory
        day_df = pd.read_csv('dashboard/data-1.csv')
        hour_df = pd.read_csv('dashboard/data-2.csv')
    
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
min_date = pd.to_datetime("2011-01-01")
max_date = pd.to_datetime("2012-12-31")

# Add date range picker
start_date = st.sidebar.date_input("Start date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End date", max_date, min_value=min_date, max_value=max_date)

# Convert to datetime for filtering
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

st.sidebar.markdown(f"<h4>Data yang ditunjukan {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} </h4>", unsafe_allow_html=True)

# Fix 2: Apply date filter to all dataframes
def filter_data_by_date(df, start_date, end_date):
    """Filter dataframe by date range"""
    mask = (df['dteday'] >= pd.Timestamp(start_date)) & (df['dteday'] <= pd.Timestamp(end_date))
    return df[mask]

# Add this after your date filter inputs in the sidebar:
filtered_day_df = filter_data_by_date(day_df, start_date, end_date)
filtered_hour_df = filter_data_by_date(hour_df, start_date, end_date)

# Menampilkan tab utama
tab1, tab2, tab3, = st.tabs([
    "☁️ Weather Impact", 
    "📅 Holiday Analysis",  
    "🕒 Hourly Trends"
])

# Tab 1: Analisis Dampak Cuaca
with tab1:
    st.markdown("<h2 class='section-header'>Weather Impact on Bike Rentals</h2>", unsafe_allow_html=True)
    
    # Grouping untuk kondisi cuaca dan jumlah sewa
    rentals_by_weather = filtered_day_df.groupby('weathersit')['cnt'].sum()

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

    # Grouping untuk kondisi cuaca dan jumlah sewa
    total_rentals_by_weather = filtered_day_df.groupby('weathersit')['cnt'].sum().sort_values(ascending=False)

    # Membuat bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    total_rentals_by_weather.plot(kind='bar', color='skyblue', edgecolor='black')

    # Menambahkan label kondisi cuaca
    weather_labels = {
        1: "Clear",
        2: "Mist/Cloudy",
        3: "Light Rain/Snow",
        4: "Heavy Rain/Snow"
    }

    # Mengatur label x-tick ke deskripsi cuaca
    plt.xticks(range(len(total_rentals_by_weather)), 
            [weather_labels.get(i, f"Weather {i}") for i in total_rentals_by_weather.index],
            rotation=90)

    # Menambah label dan judul
    plt.xlabel('Weather Condition')
    plt.ylabel('Total Number of Rentals')
    plt.title('Total Bike Rentals by Weather Condition')

    # Menambah grid line
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Menambahkan label nilai di atas setiap batang
    for i, v in enumerate(total_rentals_by_weather):
        plt.text(i, v + 30, f"{v}", ha='center')

    plt.tight_layout()
    st.pyplot(plt)

    # Grouping untuk kondisi cuaca dan rata-rata perental
    avg_rentals_by_weather = filtered_day_df.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)

    # Membuat bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    avg_rentals_by_weather.plot(kind='bar', color='skyblue', edgecolor='black')

    # Menambahkan label kondisi cuaca
    weather_labels = {
        1: "Clear",
        2: "Mist/Cloudy",
        3: "Light Rain/Snow",
        4: "Heavy Rain/Snow"
    }

    # Mengatur label x-tick ke deskripsi cuaca
    plt.xticks(range(len(avg_rentals_by_weather)), 
            [weather_labels.get(i, f"Weather {i}") for i in avg_rentals_by_weather.index],
            rotation=90)

    # Menambah label dan judul
    plt.xlabel('Weather Condition')
    plt.ylabel('Average Number of Rentals')
    plt.title('Average Bike Rentals by Weather Condition')

    # Menambah grid line
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Menambahkan label nilai di atas setiap batang
    for i, v in enumerate(avg_rentals_by_weather):
        plt.text(i, v + 30, f"{v:.1f}", ha='center')
    plt.tight_layout()
    st.pyplot(plt)

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
        workingday_comparison = filtered_day_df.groupby('workingday')[['casual', 'registered', 'cnt']].mean().reset_index()
            
        fig, ax = plt.subplots(figsize=(10, 6))
        workingday_melted = pd.melt(workingday_comparison, id_vars=['workingday'],
                                value_vars=['casual', 'registered'],
                                var_name='User Type', value_name='Average Rentals')
        
        sns.barplot(x='workingday', y='Average Rentals', hue='User Type', data=workingday_melted, ax=ax)
        
        # Menambahkan label nilai di atas setiap batang
        for i, p in enumerate(ax.patches):
            height = p.get_height()
            ax.text(p.get_x() + p.get_width()/2., height + 50,
                    f'{height:.1f}',
                    ha='center')
        ax.set_xlabel('Day Type')
        ax.set_ylabel('Average Rentals')
        ax.set_title('Average Rentals on Working Days vs. Non-Working Days')
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Dampak hari libur
        holiday_comparison = filtered_day_df.groupby('holiday')[['casual', 'registered', 'cnt']].mean().reset_index()

        fig, ax = plt.subplots(figsize=(10, 6))
        holiday_melted = pd.melt(holiday_comparison, id_vars=['holiday'], 
                                value_vars=['casual', 'registered'], 
                                var_name='User Type', value_name='Average Rentals')
        
        sns.barplot(x='holiday', y='Average Rentals', hue='User Type', data=holiday_melted, ax=ax)
        
        # Add value labels on top of each bar
        for i, p in enumerate(ax.patches):
            height = p.get_height()
            ax.text(p.get_x() + p.get_width()/2., height + 1.05,
                    f'{height:.1f}',
                    ha='center')
            
        ax.set_xlabel('Day Type')
        ax.set_ylabel('Average Rentals')
        ax.set_title('Average Rentals on Holidays vs. Regular Days')
        plt.tight_layout()
        st.pyplot(fig)
    
    # Analisis hari kerja
    st.markdown("<h3 class='subsection-header'>Rentals by Day of Week</h3>", unsafe_allow_html=True)
    
    weekday_analysis = filtered_day_df.groupby('weekday')[['casual', 'registered', 'cnt']].mean().reset_index()

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

    for bar in casual:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                f'{height:.1f}', ha='center')

    for bar in registered:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                f'{height:.1f}', ha='center')

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

# Tab 3: Hourly Rental Patterns
with tab3:
    st.markdown("<h2 class='section-header'>Hourly Rental Patterns</h2>", unsafe_allow_html=True)
    
    # Pola per jam secara keseluruhan
    st.markdown("<h3 class='subsection-header'>Total Rentals by Hour</h3>", unsafe_allow_html=True)

    # Grouping berdasarkan jam
    hourly_stats = filtered_hour_df.groupby('hr').agg({
        'cnt': 'sum', 
        'casual':['sum' ,'mean'], 
        'registered': ['sum' ,'mean'],
    }).sort_values(by=('cnt', 'sum'), ascending=False)

    # Membuat kategori waktu
    conditions = [
        (filtered_hour_df['hr'] >= 22) | (filtered_hour_df['hr'] < 5),  # Malam (10 PM - 5 AM) (22 - 5)
        (filtered_hour_df['hr'] >= 5) & (filtered_hour_df['hr'] < 11),   # Pagi (5 AM - 11 AM) (5 - 11)
        (filtered_hour_df['hr'] >= 11) & (filtered_hour_df['hr'] < 15),  # Siang (11 AM - 3 PM) (11 - 15)
        (filtered_hour_df['hr'] >= 15) & (filtered_hour_df['hr'] < 22)   # Sore (3 PM - 10 PM) (15 - 22)
    ]

    # Mendifinisikan kategori waktu
    choices = ['Malam', 'Pagi', 'Siang', 'Sore']

    # Membuat kolom baru dengan kategori waktu
    filtered_hour_df['time_of_day'] = np.select(conditions, choices, default='Unknown')

    time_analysis = filtered_hour_df.groupby('time_of_day').agg({
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

    # Fix the time of day ordering
    time_order = ['Pagi', 'Siang', 'Sore', 'Malam'] 
    time_analysis['time_of_day'] = pd.Categorical(time_analysis['time_of_day'], 
                                                categories=time_order, 
                                                ordered=True)
    time_analysis = time_analysis.sort_values('time_of_day')

    # Plot 2: Analisis Waktu Hari
    fig2, ax2 = plt.subplots(figsize=(12, 6))

    # Memasukan data untuk plotting
    seasons = time_analysis['time_of_day']
    total_rentals = time_analysis[('cnt', 'sum')]

    # Membuat X untuk posisi bar
    x = range(len(seasons))
    width = 0.6

    for i, v in enumerate(total_rentals):
        # Increase the offset percentage for more space
        y_offset = v * 0.1 # Changed from 0.02 to 0.05
        plt.text(i, v + y_offset, f"{v:,}", ha='center')

    # # After plotting all bars, adjust the y-axis limits to make room for labels
    y_max = max(total_rentals)
    ax2.set_ylim(0, y_max * 1.2)  # Add 15% extra space at the top

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
