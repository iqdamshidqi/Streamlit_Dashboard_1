# ==============================================================================
# 🇮🇩 INDONESIA NON-OIL EXPORT DASHBOARD
# ==============================================================================
# Author: Gemini
# Version: 3.0 (Merged & Refined)
# Description: A comprehensive dashboard to visualize Indonesia's non-oil 
#              export data by commodity and destination country. This script
#              is robust and includes fallbacks for optional libraries.
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np

# --- Library Import with Fallbacks ---
# Attempt to import Plotly for interactive charts; fall back to Matplotlib if not available.
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTLY_AVAILABLE = False
    st.warning("Perhatian: Pustaka 'plotly' tidak ditemukan. Beralih ke 'matplotlib' untuk visualisasi. Grafik akan menjadi statis.")

# Attempt to import PyCountry for map visualizations.
try:
    import pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False
    st.warning("Perhatian: Pustaka 'pycountry' tidak ditemukan. Fungsionalitas peta dunia tidak akan tersedia.")

# ==============================================================================
# PAGE CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(
    page_title="Indonesia Non-Oil Export Dashboard",
    page_icon="🇮🇩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a polished look and feel
st.markdown("""
<style>
    /* Main header style */
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        color: #D72323; /* Merah Bendera */
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px #cccccc;
    }
    /* Style for metric cards */
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 7px solid #1f77b4;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Sidebar style */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    /* Footer style */
    .footer {
        text-align: center;
        padding: 1rem;
        font-size: 0.9rem;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATA LOADING & PREPROCESSING
# ==============================================================================
@st.cache_data
def load_data():
    """
    Loads and preprocesses the export data from CSV files.
    This function is cached to improve performance.

    Returns:
        tuple: A tuple containing two pandas DataFrames (df_commodity, df_country).
               Returns (None, None) if data loading fails.
    """
    try:
        # --- Load Commodity Data ---
        df_commodity = pd.read_csv('ekspor_non_migas_komoditi.csv')
        # Clean up potential redundant header row
        if 'HS' in df_commodity.iloc[0].values or 'URAIAN' in df_commodity.iloc[0].values:
            df_commodity = df_commodity.iloc[1:].copy()
        
        commodity_columns = {
            'HS': 'hs_code', 'URAIAN': 'description',
            '2020': 'export_value_2020', '2021': 'export_value_2021',
            '2022': 'export_value_2022', '2023': 'export_value_2023',
            '2024': 'export_value_2024',
            'Trend (%)  2020 -  2024': 'trend_percentage_2020_2024',
            'Perub (%)  2024 -  2023': 'change_percentage_2024_2023',
            'Peran (%)  2024': 'role_percentage_2024',
            'Jan-Mei': 'export_value_jan_may_2024', 'Jan-Mei.1': 'export_value_jan_may_2025',
            'Perub (%)  2025/  2024': 'change_percentage_jan_may_2025_2024',
            'Peran (%)  2025': 'role_percentage_2025'
        }
        df_commodity.rename(columns=commodity_columns, inplace=True)

        # --- Load Country Data ---
        df_country = pd.read_csv('ekspor_non_migas_negara_english.csv')
        
        country_columns = {
            'COUNTRY': 'country',
            '2020': 'export_value_2020', '2021': 'export_value_2021',
            '2022': 'export_value_2022', '2023': 'export_value_2023',
            '2024': 'export_value_2024',
            'Trend (%) 2020 -  2024': 'trend_percentage_2020_2024',
            'Perub (%) 2024 -  2023': 'change_percentage_2024_2023',
            'Peran (%) 2024': 'role_percentage_2024',
            'Jan-Mei': 'export_value_jan_may_2024', 'Jan-Mei.1': 'export_value_jan_may_2025',
            'Perub (%) 2025/  2024': 'change_percentage_jan_may_2025_2024',
            'Peran (%) 2025': 'role_percentage_2025'
        }
        df_country.rename(columns=country_columns, inplace=True)

        # --- Convert Columns to Numeric ---
        # Identify all columns that should be numeric
        numeric_cols = [col for col in df_commodity.columns if 'export_value' in col or 'percentage' in col]
        for df in [df_commodity, df_country]:
            for col in numeric_cols:
                if col in df.columns:
                    # 'coerce' will turn non-numeric values into NaN (Not a Number)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df_commodity, df_country
    except FileNotFoundError as e:
        st.error(f"Error: File tidak ditemukan. Pastikan file 'ekspor_non_migas_komoditi.csv' dan 'ekspor_non_migas_negara_english.csv' ada di direktori yang sama.")
        st.error(f"Detail: {e}")
        return None, None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat data: {e}")
        return None, None

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def get_iso_a3(country_name):
    """
    Converts a country name to its ISO Alpha-3 code for mapping.
    Includes a manual mapping for fuzzy or non-standard names.

    Args:
        country_name (str): The name of the country.

    Returns:
        str or None: The 3-letter ISO code, or None if not found.
    """
    if not PYCOUNTRY_AVAILABLE:
        return None
        
    # Manual mapping for common mismatches or non-standard names
    country_mapping = {
        'REPUBLIC OF CHINA': 'CHN', 'UNITED STATES': 'USA', 'SOUTH KOREA': 'KOR',
        'UNITED KINGDOM': 'GBR', 'RUSSIAN FEDERATION': 'RUS', 'CZECH REPUBLIC': 'CZE',
        'BOLIVIA': 'BOL', 'VENEZUELA': 'VEN', 'IRAN': 'IRN', 'VIETNAM': 'VNM',
        "LAO PEOPLE'S DEMOCRATIC REPUBLIC": 'LAO', 'MOLDOVA': 'MDA', 'SYRIA': 'SYR',
        'TANZANIA': 'TZA', 'BRUNEI DARUSSALAM': 'BRN', 'UNITED ARAB EMIRATES': 'ARE',
        "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF": 'PRK'
    }
    
    if country_name in country_mapping:
        return country_mapping[country_name]
    
    try:
        # Use pycountry's fuzzy search for a robust match
        return pycountry.countries.search_fuzzy(country_name)[0].alpha_3
    except (LookupError, AttributeError):
        # st.warning(f"Could not find ISO code for: {country_name}")
        return None

# ==============================================================================
# CHART CREATION FUNCTIONS
# ==============================================================================
def create_trend_chart(data, data_type="commodity"):
    """Creates a trend chart for export values over the years."""
    years = sorted([int(col.split('_')[-1]) for col in data.columns if 'export_value_' in col and len(col.split('_')[-1]) == 4])
    year_columns = [f'export_value_{year}' for year in years]
    
    total_exports = [data[col].sum() for col in year_columns if col in data.columns]
    
    if PLOTLY_AVAILABLE:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years, y=total_exports, mode='lines+markers',
            name=f'Total Export Value ({data_type.title()})',
            line=dict(width=4, color='#1f77b4'), marker=dict(size=10)
        ))
        fig.update_layout(
            title=f'<b>Tren Ekspor Berdasarkan {data_type.title()}</b>',
            xaxis_title='Tahun', yaxis_title='Nilai Ekspor (Juta USD)',
            hovermode='x unified', showlegend=False, template='plotly_white'
        )
        return fig
    else:
        # Matplotlib fallback
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(years, total_exports, marker='o', linestyle='-', linewidth=3, markersize=8, color='#1f77b4')
        ax.set_title(f'Tren Ekspor Berdasarkan {data_type.title()}', fontsize=16)
        ax.set_xlabel('Tahun')
        ax.set_ylabel('Nilai Ekspor (Juta USD)')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.ticklabel_format(style='plain', axis='y')
        return fig

def create_top_items_chart(data, value_col, label_col, title, top_n=10):
    """Creates a horizontal bar chart for top N items."""
    top_data = data.nlargest(top_n, value_col).sort_values(value_col, ascending=True)
    
    if PLOTLY_AVAILABLE:
        fig = px.bar(
            top_data, x=value_col, y=label_col, orientation='h', title=f'<b>{title}</b>',
            color=value_col, color_continuous_scale=px.colors.sequential.Viridis,
            text=value_col
        )
        fig.update_layout(
            xaxis_title='Nilai Ekspor (Juta USD)', yaxis_title='',
            showlegend=False, template='plotly_white', height=500
        )
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        return fig
    else:
        # Matplotlib fallback
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(top_data[label_col], top_data[value_col], color=sns.color_palette("viridis", top_n))
        ax.set_title(title, fontsize=16)
        ax.set_xlabel('Nilai Ekspor (Juta USD)')
        ax.bar_label(bars, fmt='%.0f', padding=3)
        plt.tight_layout()
        return fig

def create_pie_chart(data, values_col, names_col, title, top_n=10):
    """Creates a pie chart for distribution."""
    top_data = data.nlargest(top_n, values_col)
    
    if PLOTLY_AVAILABLE:
        fig = px.pie(
            top_data, values=values_col, names=names_col, title=f'<b>{title}</b>',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.05] * top_n)
        return fig
    else:
        # Matplotlib fallback
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.pie(top_data[values_col], labels=top_data[names_col], autopct='%1.1f%%', startangle=90,
               colors=sns.color_palette("pastel", top_n))
        ax.set_title(title, fontsize=16)
        ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
        return fig

def create_world_map(df_country, year):
    """Creates a choropleth world map of export distribution."""
    if not PLOTLY_AVAILABLE or not PYCOUNTRY_AVAILABLE:
        return None
        
    df_country['iso_a3'] = df_country['country'].apply(get_iso_a3)
    df_map = df_country.dropna(subset=['iso_a3', f'export_value_{year}'])
    
    fig = px.choropleth(
        df_map, locations="iso_a3", color=f"export_value_{year}",
        hover_name="country", hover_data={f"export_value_{year}": ":,.0f"},
        color_continuous_scale="Plasma",
        title=f"<b>Distribusi Ekspor Global ({year})</b>"
    )
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'),
        height=600, template='plotly_white'
    )
    return fig

# ==============================================================================
# MAIN APPLICATION LOGIC
# ==============================================================================
def main():
    """
    The main function that runs the Streamlit application.
    """
    # --- Header ---
    st.markdown('<p class="main-header">🇮🇩 Dasbor Ekspor Non-Migas Indonesia</p>', unsafe_allow_html=True)
    
    # --- Data Loading ---
    df_commodity, df_country = load_data()
    if df_commodity is None or df_country is None:
        st.warning("Tidak dapat melanjutkan karena data gagal dimuat.")
        return
    
    # --- Sidebar Filters ---
    st.sidebar.header("🎛️ Filter Dasbor")
    available_years = sorted([int(col.split('_')[-1]) for col in df_commodity.columns if 'export_value_' in col and len(col.split('_')[-1]) == 4])
    selected_year = st.sidebar.selectbox(
        "Pilih Tahun Analisis", available_years, index=len(available_years)-1
    )
    
    analysis_type = st.sidebar.radio(
        "Pilih Jenis Analisis",
        ["Ringkasan Umum", "Analisis Komoditas", "Analisis Negara Tujuan", "Analisis Komparatif"]
    )
    
    # --- Dynamic UI based on Analysis Type ---
    st.markdown("---")
    
    if analysis_type == "Ringkasan Umum":
        st.header("📈 Ringkasan Umum Ekspor")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        current_year_col = f'export_value_{selected_year}'
        
        total_commodity_export = df_commodity[current_year_col].sum()
        total_country_export = df_country[current_year_col].sum()
        
        with col1:
            st.metric("Total Ekspor (by Commodity)", f"${total_commodity_export:,.0f} Juta")
        with col2:
            st.metric("Total Ekspor (by Country)", f"${total_country_export:,.0f} Juta")
        with col3:
            st.metric("Jumlah Jenis Komoditas", len(df_commodity))
        with col4:
            st.metric("Jumlah Negara Tujuan", len(df_country))
            
        st.markdown("<br>", unsafe_allow_html=True)

        # Trend charts
        col1, col2 = st.columns(2)
        with col1:
            commodity_trend = create_trend_chart(df_commodity, "Komoditas")
            st.plotly_chart(commodity_trend, use_container_width=True) if PLOTLY_AVAILABLE else st.pyplot(commodity_trend)
        with col2:
            country_trend = create_trend_chart(df_country, "Negara")
            st.plotly_chart(country_trend, use_container_width=True) if PLOTLY_AVAILABLE else st.pyplot(country_trend)
        
        # World map
        st.header("🗺️ Peta Distribusi Ekspor Global")
        world_map = create_world_map(df_country, selected_year)
        if world_map:
            st.plotly_chart(world_map, use_container_width=True)
        else:
            st.info("Peta tidak dapat ditampilkan karena 'plotly' atau 'pycountry' tidak terpasang.")

    elif analysis_type == "Analisis Komoditas":
        st.header("🏭 Analisis Ekspor Berdasarkan Komoditas")
        
        top_n_commodities = st.sidebar.slider("Jumlah Komoditas Teratas", 5, 30, 10)
        
        current_year_col = f'export_value_{selected_year}'
        
        # Top commodities bar chart
        top_commodities_chart = create_top_items_chart(
            df_commodity, current_year_col, 'description',
            f'{top_n_commodities} Komoditas Ekspor Teratas ({selected_year})', top_n_commodities
        )
        st.plotly_chart(top_commodities_chart, use_container_width=True) if PLOTLY_AVAILABLE else st.pyplot(top_commodities_chart)
            
        col1, col2 = st.columns([1, 1])
        with col1:
            # Pie chart for distribution
            pie_chart = create_pie_chart(
                df_commodity, current_year_col, 'description',
                f'Distribusi Ekspor {top_n_commodities} Komoditas Teratas ({selected_year})', top_n_commodities
            )
            st.plotly_chart(pie_chart, use_container_width=True) if PLOTLY_AVAILABLE else st.pyplot(pie_chart)
        with col2:
            # Data table
            st.subheader(f"Data {top_n_commodities} Komoditas Teratas")
            top_data = df_commodity.nlargest(top_n_commodities, current_year_col)[
                ['description', current_year_col, f'role_percentage_{selected_year}']
            ].rename(columns={
                'description': 'Deskripsi',
                current_year_col: f'Nilai {selected_year}',
                f'role_percentage_{selected_year}': f'Peran (%) {selected_year}'
            }).round(2)
            st.dataframe(top_data, use_container_width=True)

    elif analysis_type == "Analisis Negara Tujuan":
        st.header("🌍 Analisis Ekspor Berdasarkan Negara Tujuan")
        
        top_n_countries = st.sidebar.slider("Jumlah Negara Teratas", 5, 30, 10)
        
        current_year_col = f'export_value_{selected_year}'
        
        # Top countries bar chart
        top_countries_chart = create_top_items_chart(
            df_country, current_year_col, 'country',
            f'{top_n_countries} Negara Tujuan Ekspor Teratas ({selected_year})', top_n_countries
        )
        st.plotly_chart(top_countries_chart, use_container_width=True) if PLOTLY_AVAILABLE else st.pyplot(top_countries_chart)
            
        col1, col2 = st.columns([1, 1])
        with col1:
            # Pie chart for distribution
            pie_chart = create_pie_chart(
                df_country, current_year_col, 'country',
                f'Distribusi Ekspor {top_n_countries} Negara Teratas ({selected_year})', top_n_countries
            )
            st.plotly_chart(pie_chart, use_container_width=True) if PLOTLY_AVAILABLE else st.pyplot(pie_chart)
        with col2:
            # Data table
            st.subheader(f"Data {top_n_countries} Negara Teratas")
            top_data = df_country.nlargest(top_n_countries, current_year_col)[
                ['country', current_year_col, f'role_percentage_{selected_year}']
            ].rename(columns={
                'country': 'Negara',
                current_year_col: f'Nilai {selected_year}',
                f'role_percentage_{selected_year}': f'Peran (%) {selected_year}'
            }).round(2)
            st.dataframe(top_data, use_container_width=True)

    elif analysis_type == "Analisis Komparatif":
        st.header("⚖️ Analisis Komparatif (Year-over-Year)")
        
        if selected_year > min(available_years):
            prev_year = selected_year - 1
            current_col = f'export_value_{selected_year}'
            prev_col = f'export_value_{prev_year}'
            
            st.subheader(f"Perbandingan Ekspor: {selected_year} vs {prev_year}")
            
            col1, col2 = st.columns(2)
            
            # Commodity comparison
            with col1:
                if current_col in df_commodity.columns and prev_col in df_commodity.columns:
                    current_total = df_commodity[current_col].sum()
                    prev_total = df_commodity[prev_col].sum()
                    change = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
                    st.metric(
                        f"Total Ekspor Komoditas ({selected_year})",
                        f"${current_total:,.0f} Juta",
                        f"{change:+.2f}% vs {prev_year}"
                    )
            
            # Country comparison
            with col2:
                if current_col in df_country.columns and prev_col in df_country.columns:
                    current_total = df_country[current_col].sum()
                    prev_total = df_country[prev_col].sum()
                    change = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
                    st.metric(
                        f"Total Ekspor ke Negara ({selected_year})",
                        f"${current_total:,.0f} Juta",
                        f"{change:+.2f}% vs {prev_year}"
                    )
            
            st.markdown("---")
            st.subheader(f"Perbandingan Performa Teratas di {selected_year}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**5 Komoditas Teratas ({selected_year})**")
                top_commodities = df_commodity.nlargest(5, current_col)[['description', current_col]].round(2)
                st.dataframe(top_commodities, use_container_width=True)
            with col2:
                st.write(f"**5 Negara Tujuan Teratas ({selected_year})**")
                top_countries = df_country.nlargest(5, current_col)[['country', current_col]].round(2)
                st.dataframe(top_countries, use_container_width=True)
        else:
            st.info(f"Tidak ada data tahun sebelumnya untuk dibandingkan dengan {selected_year}.")

    # --- Footer ---
    st.markdown("---")
    st.markdown(
        """
        <div class="footer">
            📊 <b>Dasbor Ekspor Non-Migas Indonesia</b> | 
            Sumber Data: Kementerian Perdagangan Republik Indonesia | 
            Dibuat dengan Streamlit & Plotly
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
