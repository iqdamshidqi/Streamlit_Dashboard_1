import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# --- Pengecekan dependensi opsional ---
try:
    import pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False

# Set PLOTLY_AVAILABLE to True since we are using it directly
PLOTLY_AVAILABLE = True


# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Indonesia Non-Oil Export Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- CSS Kustom yang Ditingkatkan ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Custom Font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Header */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Enhanced Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Filter Section */
    .filter-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
    }
    
    /* Chart Container */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }
    
    /* Statistics Box */
    .stats-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stats-box h3 {
        margin: 0 0 1rem 0;
        font-weight: 600;
    }
    
    .stats-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.2);
    }
    
    .stats-item:last-child {
        border-bottom: none;
    }
    
    /* Alert Boxes */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Data Table Styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #667eea 50%, transparent 100%);
        margin: 2rem 0;
        border: none;
    }
    
    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .metric-value {
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# --- Fungsi-Fungsi Helper yang Ditingkatkan ---

@st.cache_data
def load_data():
    """Memuat dan memproses data ekspor."""
    try:
        with st.spinner("🔄 Loading data..."):
            df_commodity = pd.read_csv('ekspor_non_migas_komoditi.csv')
            if df_commodity.iloc[0].astype(str).str.contains('HS|URAIAN').any():
                df_commodity = df_commodity.iloc[1:].copy()
            
            commodity_columns = {
                'HS': 'hs_code', 'URAIAN': 'description', '2020': 'export_value_2020',
                '2021': 'export_value_2021', '2022': 'export_value_2022', '2023': 'export_value_2023',
                '2024': 'export_value_2024', 'Trend (%)  2020 -  2024': 'trend_percentage_2020_2024',
                'Perub (%)  2024 -  2023': 'change_percentage_2024_2023', 'Peran (%)  2024': 'role_percentage_2024',
                'Jan-Mei': 'export_value_jan_may_2024', 'Jan-Mei.1': 'export_value_jan_may_2025',
                'Perub (%)  2025/  2024': 'change_percentage_jan_may_2025_2024', 'Peran (%)  2025': 'role_percentage_2025'
            }
            df_commodity.rename(columns=commodity_columns, inplace=True)

            df_country = pd.read_csv('ekspor_non_migas_negara_english.csv')
            country_columns = {
                'COUNTRY': 'country', '2020': 'export_value_2020', '2021': 'export_value_2021',
                '2022': 'export_value_2022', '2023': 'export_value_2023', '2024': 'export_value_2024',
                'Trend (%) 2020 -  2024': 'trend_percentage_2020_2024', 'Perub (%) 2024 -  2023': 'change_percentage_2024_2023',
                'Peran (%) 2024': 'role_percentage_2024', 'Jan-Mei': 'export_value_jan_may_2024',
                'Jan-Mei.1': 'export_value_jan_may_2025', 'Perub (%) 2025/  2024': 'change_percentage_jan_may_2025_2024',
                'Peran (%) 2025': 'role_percentage_2025'
            }
            df_country.rename(columns=country_columns, inplace=True)

            numeric_cols = [col for col in commodity_columns.values() if 'export_value' in col or 'percentage' in col]
            for col in numeric_cols:
                if col in df_commodity.columns:
                    df_commodity[col] = pd.to_numeric(df_commodity[col], errors='coerce')
                if col in df_country.columns:
                    df_country[col] = pd.to_numeric(df_country[col], errors='coerce')
            
        return df_commodity, df_country
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None, None

def create_enhanced_metric_card(title, value, icon="📊", delta=None, delta_color="normal"):
    """Membuat kartu metrik yang ditingkatkan."""
    delta_html = ""
    if delta is not None:
        color = "#28a745" if delta_color == "normal" and delta > 0 else "#dc3545" if delta < 0 else "#6c757d"
        delta_html = f'<div style="color: {color}; font-size: 0.8rem; margin-top: 0.5rem;">{"↗️" if delta > 0 else "↘️" if delta < 0 else "➡️"} {delta:+.1f}%</div>'
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def create_streamlit_bar_chart(data, value_col, label_col, title, top_n=10):
    """Membuat bar chart menggunakan fungsi bawaan Streamlit dengan styling yang ditingkatkan."""
    st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
    top_data = data.nlargest(top_n, value_col).copy()
    top_data = top_data.set_index(label_col)
    st.subheader(f"📊 {title}")
    st.bar_chart(top_data[value_col], color="#667eea")
    st.markdown('</div>', unsafe_allow_html=True)
    return top_data

def create_streamlit_line_chart(data, data_type="commodity"):
    """Membuat line chart menggunakan fungsi bawaan Streamlit dengan styling yang ditingkatkan."""
    st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
    years = [2020, 2021, 2022, 2023, 2024]
    year_columns = [f'export_value_{year}' for year in years]
    trend_data = {years[i]: data[col].sum() if col in data.columns else 0 for i, col in enumerate(year_columns)}
    trend_df = pd.DataFrame(list(trend_data.items()), columns=['Year', 'Export_Value'])
    trend_df['Year'] = trend_df['Year'].astype(str)
    trend_df = trend_df.set_index('Year')
    st.subheader(f'📈 Export Trend Over Time - {data_type.title()}')
    st.line_chart(trend_df, color="#667eea")
    st.markdown('</div>', unsafe_allow_html=True)
    return trend_df

def get_iso_a3(country_name):
    """Mengonversi nama negara ke kode ISO Alpha-3."""
    if not PYCOUNTRY_AVAILABLE:
        return None
    country_mapping = {
        'REPUBLIC OF CHINA': 'CHN', 'UNITED STATES': 'USA', 'SOUTH KOREA': 'KOR', 'UNITED KINGDOM': 'GBR',
        'RUSSIAN FEDERATION': 'RUS', 'CZECH REPUBLIC': 'CZE', 'BOLIVIA': 'BOL', 'VENEZUELA': 'VEN',
        'IRAN': 'IRN', "LAO PEOPLE'S DEMOCRATIC REPUBLIC": 'LAO', 'MOLDOVA': 'MDA', 'SYRIA': 'SYR',
        'TANZANIA': 'TZA', 'VIETNAM': 'VNM', 'BRUNEI DARUSSALAM': 'BRN', 'CABO VERDE': 'CPV', 'CONGO': 'COG',
        'DEMOCRATIC REPUBLIC OF THE CONGO': 'COD', 'EGYPT': 'EGY', 'GAMBIA': 'GMB', 'GUINEA BISSAU': 'GNB',
        'SAO TOME AND PRINCIPE': 'STP', 'SWAZILAND': 'SWZ', 'UNITED ARAB EMIRATES': 'ARE', 'YEMEN': 'YEM',
        'NORTH MACEDONIA': 'MKD', 'PALESTINE': 'PSE', "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF": 'PRK'
    }
    if country_name in country_mapping:
        return country_mapping[country_name]
    try:
        return pycountry.countries.search_fuzzy(country_name)[0].alpha_3
    except LookupError:
        return None

def create_data_table(data, value_col, label_col, title, top_n=10):
    """Membuat tabel data yang diformat dengan styling yang ditingkatkan."""
    st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
    top_data = data.nlargest(top_n, value_col)
    display_data = top_data[[label_col, value_col]].copy()
    display_data[value_col] = display_data[value_col].apply(lambda x: f"${x:,.0f}M")
    display_data.columns = [label_col.replace('_', ' ').title(), 'Export Value']
    st.subheader(f"📋 {title}")
    st.dataframe(display_data, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    return display_data

def format_number(num):
    """Memformat angka besar dengan sufiks yang sesuai."""
    if num >= 1e9:
        return f"${num/1e9:.1f}B"
    elif num >= 1e6:
        return f"${num/1e6:.1f}M"
    elif num >= 1e3:
        return f"${num/1e3:.1f}K"
    else:
        return f"${num:.0f}"

def calculate_growth_rate(current, previous):
    """Menghitung tingkat pertumbuhan antara dua periode."""
    if previous == 0 or pd.isna(previous) or pd.isna(current):
        return 0
    return ((current - previous) / previous) * 100

def create_world_map(df_country, year, highlighted_countries=None):
    """Membuat visualisasi peta dunia dengan highlight opsional dan styling yang ditingkatkan."""
    if not PYCOUNTRY_AVAILABLE:
        st.warning("🗺️ World map requires pycountry library")
        return None
    
    df_country['iso_a3'] = df_country['country'].apply(get_iso_a3)
    df_map = df_country.dropna(subset=['iso_a3'])
    color_col = f"export_value_{year}"
    
    if color_col not in df_map.columns:
        st.warning(f"⚠️ Data for year {year} not available for the map.")
        return None
    
    fig = px.choropleth(
        df_map, locations="iso_a3", color=color_col, hover_name="country",
        hover_data={color_col: ":,.0f"}, 
        color_continuous_scale="Viridis",
        title=f"🌍 Export Distribution by Country ({year})"
    )
    
    if highlighted_countries:
        highlight_df = df_map[df_map['country'].isin(highlighted_countries)]
        if not highlight_df.empty:
            fig.add_trace(go.Scattergeo(
                locations=highlight_df['iso_a3'], mode='markers',
                marker=dict(size=12, color='#ff6b6b', line=dict(width=2, color='white')),
                hoverinfo='text', text=highlight_df['country'], name='Selected Countries'
            ))
    
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'),
        height=500,
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
        title_font_size=16,
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_donut_chart_with_total(data, values_col, names_col, title, top_n=10):
    """Membuat donut chart dengan total nilai di tengah dan styling yang ditingkatkan."""
    if data.empty or values_col not in data.columns:
        st.warning("⚠️ Data tidak tersedia untuk membuat chart.")
        return None
    
    top_data = data.nlargest(top_n, values_col)
    total_value = top_data[values_col].sum()
    formatted_total = format_number(total_value)
    
    # Custom color palette
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', 
              '#43e97b', '#38f9d7', '#ffecd2', '#fcb69f']
    
    fig = px.pie(
        top_data, values=values_col, names=names_col, title=title,
        hole=0.4, color_discrete_sequence=colors
    )
    
    fig.update_traces(
        textposition='outside', 
        textinfo='percent+label', 
        pull=[0.02] * top_n,
        textfont_size=12,
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    
    fig.update_layout(
        showlegend=False,
        annotations=[dict(
            text=f"<b>Total</b><br>{formatted_total}", 
            x=0.5, y=0.5, 
            font_size=18, 
            showarrow=False,
            font_color='#2c3e50'
        )],
        title_font_size=16,
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    return fig

def create_enhanced_sidebar():
    """Membuat sidebar yang ditingkatkan dengan styling yang lebih baik."""
    st.sidebar.markdown("""
    <div class="filter-section">
        <h2 style="color: #2c3e50; margin-bottom: 1rem;">🎛️ Dashboard Controls</h2>
    </div>
    """, unsafe_allow_html=True)

def create_section_header(title, icon="📊"):
    """Membuat header section yang konsisten."""
    st.markdown(f"""
    <div class="section-header">
        <span>{icon}</span>
        <span>{title}</span>
    </div>
    """, unsafe_allow_html=True)

def create_stats_summary(data, current_year_col, title="📊 Statistical Summary"):
    """Membuat ringkasan statistik yang menarik."""
    total_export = data[current_year_col].sum()
    avg_export = data[current_year_col].mean()
    max_export = data[current_year_col].max()
    min_export = data[current_year_col].min()
    
    st.markdown(f"""
    <div class="stats-box">
        <h3>{title}</h3>
        <div class="stats-item">
            <span>💰 Total Export</span>
            <span><strong>{format_number(total_export)}</strong></span>
        </div>
        <div class="stats-item">
            <span>📊 Average Export</span>
            <span><strong>{format_number(avg_export)}</strong></span>
        </div>
        <div class="stats-item">
            <span>🏆 Highest Export</span>
            <span><strong>{format_number(max_export)}</strong></span>
        </div>
        <div class="stats-item">
            <span>📉 Lowest Export</span>
            <span><strong>{format_number(min_export)}</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- Aplikasi Utama yang Ditingkatkan ---

def main():
    # Header utama dengan styling yang ditingkatkan
    st.markdown('<p class="main-header">🇮🇩 Indonesia Non-Oil Export Dashboard</p>', unsafe_allow_html=True)
    
    # Load data dengan loading indicator
    df_commodity, df_country = load_data()
    if df_commodity is None or df_country is None:
        st.error("❌ Failed to load data. Please check your data files.")
        return

    # Sidebar yang ditingkatkan
    create_enhanced_sidebar()
    
    available_years = [2020, 2021, 2022, 2023, 2024]
    selected_year = st.sidebar.selectbox("📅 Select Year", available_years, index=len(available_years)-1)
    
    analysis_type = st.sidebar.radio(
        "🔍 Select Analysis Type",
        ["📊 Overview", "🏭 Commodity Analysis", "🌍 Country Analysis", "⚖️ Comparative Analysis"]
    )

    # Filter berdasarkan jenis analisis
    if analysis_type == "🏭 Commodity Analysis":
        st.sidebar.markdown("### 🏭 Commodity Filters")
        top_n_commodities = st.sidebar.slider("Number of Top Commodities", 5, 20, 10)
        commodity_filter = st.sidebar.multiselect(
            "Filter by Commodity", options=df_commodity['description'].unique(), default=[]
        )
    elif analysis_type == "🌍 Country Analysis":
        st.sidebar.markdown("### 🌍 Country Filters")
        top_n_countries = st.sidebar.slider("Number of Top Countries", 5, 20, 10)
        country_filter = st.sidebar.multiselect(
            "Filter by Country", options=df_country['country'].unique(), default=[]
        )

    current_year_col = f'export_value_{selected_year}'

    # Overview Section
    if analysis_type == "📊 Overview":
        create_section_header("Export Overview", "📈")
        
        # Enhanced metric cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            commodity_total = df_commodity[current_year_col].sum()
            prev_year_col = f'export_value_{selected_year-1}' if selected_year > 2020 else None
            delta = None
            if prev_year_col and prev_year_col in df_commodity.columns:
                prev_total = df_commodity[prev_year_col].sum()
                delta = calculate_growth_rate(commodity_total, prev_total)
            create_enhanced_metric_card("Total Commodity Export", format_number(commodity_total), "🏭", delta)
        
        with col2:
            country_total = df_country[current_year_col].sum()
            delta = None
            if prev_year_col and prev_year_col in df_country.columns:
                prev_total = df_country[prev_year_col].sum()
                delta = calculate_growth_rate(country_total, prev_total)
            create_enhanced_metric_card("Total Country Export", format_number(country_total), "🌍", delta)
        
        with col3:
            create_enhanced_metric_card("Total Commodities", f"{len(df_commodity):,}", "📦")
        
        with col4:
            create_enhanced_metric_card("Export Destinations", f"{len(df_country):,}", "🎯")

        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

        # Trend charts
        col1, col2 = st.columns(2)
        with col1:
            create_streamlit_line_chart(df_commodity, "Commodity")
        with col2:
            create_streamlit_line_chart(df_country, "Country")

        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

        # Top contributors section
        create_section_header(f"Top 10 Contributors in {selected_year}", "🏆")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            commodity_donut = create_donut_chart_with_total(
                df_commodity, current_year_col, 'description',
                "🏭 Commodity Distribution", top_n=10
            )
            if commodity_donut:
                st.plotly_chart(commodity_donut, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            country_donut = create_donut_chart_with_total(
                df_country, current_year_col, 'country',
                "🌍 Country Distribution", top_n=10
            )
            if country_donut:
                st.plotly_chart(country_donut, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
        
        # World map
        create_section_header(f"Global Export Distribution ({selected_year})", "🗺️")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        world_map = create_world_map(df_country, selected_year)
        if world_map:
            st.plotly_chart(world_map, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Commodity Analysis Section
    elif analysis_type == "🏭 Commodity Analysis":
        create_section_header("Commodity Export Analysis", "🏭")
        
        filtered_df = df_commodity.copy()
        if commodity_filter:
            filtered_df = filtered_df[filtered_df['description'].isin(commodity_filter)]

        if current_year_col in filtered_df.columns and not filtered_df.empty:
            # Donut chart
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader(f"📈 Distribution of Top {top_n_commodities} Commodities ({selected_year})")
            donut_fig = create_donut_chart_with_total(
                filtered_df, current_year_col, 'description',
                f"Top {top_n_commodities} Commodities Export Share", top_n_commodities
            )
            if donut_fig:
                st.plotly_chart(donut_fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

            col1, col2 = st.columns([2, 1])
            with col1:
                create_streamlit_bar_chart(
                    filtered_df, current_year_col, 'description',
                    f'Top {top_n_commodities} Commodity Exports ({selected_year})', top_n_commodities
                )
            with col2:
                create_stats_summary(filtered_df, current_year_col, "📊 Commodity Statistics")
                
            create_data_table(
                filtered_df, current_year_col, 'description',
                f"Detailed Commodity Data ({selected_year})", top_n_commodities
            )
        else:
            st.markdown("""
            <div class="warning-box">
                ⚠️ No data available to display with the selected filters.
            </div>
            """, unsafe_allow_html=True)

    # Country Analysis Section
    elif analysis_type == "🌍 Country Analysis":
        create_section_header("Country Export Analysis", "🌍")
        
        filtered_df = df_country.copy()
        if country_filter:
            filtered_df = filtered_df[filtered_df['country'].isin(country_filter)]
            
        if current_year_col in df_country.columns and not df_country.empty:
            # Donut chart
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader(f"📈 Distribution of Top {top_n_countries} Destination Countries ({selected_year})")
            donut_fig = create_donut_chart_with_total(
                filtered_df, current_year_col, 'country',
                f"Top {top_n_countries} Destination Countries Export Share", top_n_countries
            )
            if donut_fig:
                st.plotly_chart(donut_fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

            # World map with highlights
            create_section_header(f"Global Export Distribution Map ({selected_year})", "🗺️")
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            world_map_fig = create_world_map(df_country, selected_year, highlighted_countries=country_filter)
            if world_map_fig:
                st.plotly_chart(world_map_fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

            col1, col2 = st.columns([2, 1])
            with col1:
                create_streamlit_bar_chart(
                    filtered_df, current_year_col, 'country',
                    f'Top {top_n_countries} Destination Countries ({selected_year})', top_n_countries
                )
            with col2:
                create_stats_summary(filtered_df, current_year_col, "📊 Country Statistics")

            create_data_table(
                filtered_df, current_year_col, 'country',
                f"Detailed Country Data ({selected_year})", top_n_countries
            )
        else:
            st.markdown("""
            <div class="warning-box">
                ⚠️ No data available to display with the selected filters.
            </div>
            """, unsafe_allow_html=True)

    # Comparative Analysis Section
    elif analysis_type == "⚖️ Comparative Analysis":
        create_section_header("Comparative Analysis", "⚖️")
        
        if selected_year > 2020:
            prev_year = selected_year - 1
            prev_col = f'export_value_{prev_year}'
            
            # Enhanced comparison metrics
            col1, col2, col3, col4 = st.columns(4)
            
            current_total_comm = df_commodity[current_year_col].sum()
            prev_total_comm = df_commodity[prev_col].sum()
            comm_growth = calculate_growth_rate(current_total_comm, prev_total_comm)
            
            current_total_country = df_country[current_year_col].sum()
            prev_total_country = df_country[prev_col].sum()
            country_growth = calculate_growth_rate(current_total_country, prev_total_country)
            
            with col1:
                create_enhanced_metric_card(
                    f"Commodity Export ({selected_year})", 
                    format_number(current_total_comm), 
                    "🏭", 
                    comm_growth
                )
            
            with col2:
                create_enhanced_metric_card(
                    f"Commodity Export ({prev_year})", 
                    format_number(prev_total_comm), 
                    "🏭"
                )
            
            with col3:
                create_enhanced_metric_card(
                    f"Country Export ({selected_year})", 
                    format_number(current_total_country), 
                    "🌍", 
                    country_growth
                )
            
            with col4:
                create_enhanced_metric_card(
                    f"Country Export ({prev_year})", 
                    format_number(prev_total_country), 
                    "🌍"
                )

            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

            # Growth analysis
            if comm_growth > 0:
                st.markdown(f"""
                <div class="success-box">
                    📈 <strong>Positive Growth!</strong> Commodity exports grew by <strong>{comm_growth:.1f}%</strong> from {prev_year} to {selected_year}.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="warning-box">
                    📉 <strong>Decline Alert:</strong> Commodity exports decreased by <strong>{abs(comm_growth):.1f}%</strong> from {prev_year} to {selected_year}.
                </div>
                """, unsafe_allow_html=True)

            # Comparison charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Top commodities comparison
                top_commodities_current = df_commodity.nlargest(10, current_year_col)
                comparison_data = top_commodities_current[['description', current_year_col, prev_col]].copy()
                comparison_data.columns = ['Commodity', f'{selected_year}', f'{prev_year}']
                comparison_data = comparison_data.set_index('Commodity')
                
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.subheader(f"📊 Top 10 Commodities Comparison")
                st.bar_chart(comparison_data)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # Top countries comparison
                top_countries_current = df_country.nlargest(10, current_year_col)
                comparison_data_country = top_countries_current[['country', current_year_col, prev_col]].copy()
                comparison_data_country.columns = ['Country', f'{selected_year}', f'{prev_year}']
                comparison_data_country = comparison_data_country.set_index('Country')
                
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.subheader(f"🌍 Top 10 Countries Comparison")
                st.bar_chart(comparison_data_country)
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="warning-box">
                ⚠️ Comparative analysis requires data from at least two years. Please select a year after 2020.
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem 0;">
        <p>📊 Indonesia Non-Oil Export Dashboard | Data Analysis & Visualization</p>
        <p style="font-size: 0.8rem;">Built with Streamlit & Plotly | Enhanced UI/UX Design</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

