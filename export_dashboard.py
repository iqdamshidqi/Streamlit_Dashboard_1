import streamlit as st
import pandas as pd
import numpy as np

# Mencoba impor plotly, jika gagal akan menggunakan alternatif
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    # Matplotlib tetap dibutuhkan khusus untuk alternatif pie chart
    import matplotlib.pyplot as plt 
    PLOTLY_AVAILABLE = False
    st.warning("Plotly tidak tersedia. Menggunakan chart bawaan Streamlit & Matplotlib sebagai alternatif.")

# Mencoba impor pycountry untuk fungsionalitas peta dunia
try:
    import pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False
    st.warning("Pycountry tidak tersedia, fungsionalitas peta dunia akan terbatas.")

# Konfigurasi halaman
st.set_page_config(
    page_title="Indonesia Non-Oil Export Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Kustom
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Memuat dan memproses data ekspor dari file CSV."""
    try:
        # Muat data komoditas
        df_commodity = pd.read_csv('ekspor_non_migas_komoditi.csv')
        if df_commodity.iloc[0].astype(str).str.contains('HS|URAIAN').any():
            df_commodity = df_commodity.iloc[1:].copy()
        
        commodity_columns = {
            'HS': 'hs_code', 'URAIAN': 'description', '2020': 'export_value_2020',
            '2021': 'export_value_2021', '2022': 'export_value_2022', '2023': 'export_value_2023',
            '2024': 'export_value_2024', 'Trend (%)  2020 -  2024': 'trend_percentage_2020_2024',
            'Perub (%)  2024 -  2023': 'change_percentage_2024_2023', 'Peran (%)  2024': 'role_percentage_2024',
        }
        df_commodity.rename(columns=commodity_columns, inplace=True)
        
        # Muat data negara
        df_country = pd.read_csv('ekspor_non_migas_negara_english.csv')
        country_columns = {
            'COUNTRY': 'country', '2020': 'export_value_2020', '2021': 'export_value_2021',
            '2022': 'export_value_2022', '2023': 'export_value_2023', '2024': 'export_value_2024',
            'Trend (%) 2020 -  2024': 'trend_percentage_2020_2024', 'Perub (%) 2024 -  2023': 'change_percentage_2024_2023',
            'Peran (%) 2024': 'role_percentage_2024',
        }
        df_country.rename(columns=country_columns, inplace=True)
        
        # Konversi kolom numerik
        numeric_cols = [col for col in df_commodity.columns if 'export_value' in col or 'percentage' in col]
        for col in numeric_cols:
            if col in df_commodity.columns:
                df_commodity[col] = pd.to_numeric(df_commodity[col], errors='coerce')
            if col in df_country.columns:
                df_country[col] = pd.to_numeric(df_country[col], errors='coerce')
        
        return df_commodity, df_country
    except FileNotFoundError as e:
        st.error(f"Error: File tidak ditemukan. Pastikan file 'ekspor_non_migas_komoditi.csv' dan 'ekspor_non_migas_negara_english.csv' ada di direktori yang sama.")
        return None, None
    except Exception as e:
        st.error(f"Terjadi error saat memuat data: {str(e)}")
        return None, None

def get_iso_a3(country_name):
    """Mengonversi nama negara ke kode ISO Alpha-3."""
    if not PYCOUNTRY_AVAILABLE: return None
    country_mapping = {
        'REPUBLIC OF CHINA': 'CHN', 'UNITED STATES': 'USA', 'SOUTH KOREA': 'KOR',
        'UNITED KINGDOM': 'GBR', 'RUSSIAN FEDERATION': 'RUS'
    }
    if country_name in country_mapping: return country_mapping[country_name]
    try:
        return pycountry.countries.search_fuzzy(country_name)[0].alpha_3
    except LookupError:
        return None

def create_trend_chart(data, data_type="commodity"):
    """Membuat grafik tren nilai ekspor selama beberapa tahun."""
    years = [2020, 2021, 2022, 2023, 2024]
    year_columns = [f'export_value_{year}' for year in years]
    total_exports = [data[col].sum() if col in data.columns else 0 for col in year_columns]
    
    chart_data = pd.DataFrame({
        'Year': years,
        'Total Export Value': total_exports
    }).set_index('Year')

    if PLOTLY_AVAILABLE:
        fig = px.line(
            chart_data, y='Total Export Value',
            title=f'Tren Ekspor Berdasarkan {data_type.title()}', markers=True
        )
        fig.update_layout(hovermode='x unified')
        return "plotly", fig
    else:
        # Alternatif: chart garis bawaan Streamlit
        return "streamlit_native", chart_data

def create_top_items_chart(data, value_col, label_col, title, top_n=10):
    """Membuat grafik batang untuk item teratas."""
    top_data = data.nlargest(top_n, value_col).sort_values(value_col)
    
    if PLOTLY_AVAILABLE:
        fig = px.bar(
            top_data, x=value_col, y=label_col, orientation='h', title=title,
            color=value_col, color_continuous_scale='viridis'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
        return "plotly", fig
    else:
        # Alternatif: chart batang bawaan Streamlit
        chart_data = top_data.set_index(label_col)[[value_col]]
        return "streamlit_native", chart_data

def create_pie_chart(data, values_col, names_col, title, top_n=10):
    """Membuat diagram lingkaran untuk distribusi."""
    top_data = data.nlargest(top_n, values_col)
    
    if PLOTLY_AVAILABLE:
        fig = px.pie(
            top_data, values=values_col, names=names_col, title=title,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return "plotly", fig
    else:
        # Alternatif: Matplotlib (karena Streamlit tidak punya pie chart bawaan)
        st.subheader(title) 
        fig, ax = plt.subplots()
        ax.pie(top_data[values_col], labels=top_data[names_col], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        return "matplotlib", fig

def create_choropleth_map(input_df, selected_year):
    """Membuat visualisasi peta dunia."""
    if not PLOTLY_AVAILABLE or not PYCOUNTRY_AVAILABLE:
        st.warning("Peta Dunia memerlukan library Plotly dan PyCountry.")
        return None
        
    df_map = input_df.copy()
    df_map['iso_a3'] = df_map['country'].apply(get_iso_a3)
    df_map.dropna(subset=['iso_a3'], inplace=True)
    
    color_col = f'export_value_{selected_year}'
    
    fig = px.choropleth(
        df_map, locations="iso_a3", color=color_col,
        hover_name="country", hover_data={color_col: ":,.0f"},
        color_continuous_scale="plasma",
        title=f"Distribusi Ekspor Global Berdasarkan Negara ({selected_year})"
    )
    fig.update_layout(geo=dict(showframe=False, showcoastlines=True))
    return fig

def main():
    """Fungsi utama untuk menjalankan dashboard Streamlit."""
    st.markdown('<p class="main-header">🇮🇩 Dashboard Ekspor Non-Migas Indonesia</p>', unsafe_allow_html=True)
    
    df_commodity, df_country = load_data()
    if df_commodity is None or df_country is None: 
        return

    # --- Sidebar ---
    st.sidebar.header("🎛️ Filter Dashboard")
    available_years = [2020, 2021, 2022, 2023, 2024]
    selected_year = st.sidebar.selectbox("Pilih Tahun Analisis", available_years, index=len(available_years)-1)
    
    analysis_type = st.sidebar.radio("Pilih Jenis Analisis", ["Ringkasan", "Analisis Komoditas", "Analisis Negara"])
    
    # --- Konten Utama ---
    if analysis_type == "Ringkasan":
        st.header("📈 Ringkasan Ekspor")
        col1, col2 = st.columns(2)
        
        with col1:
            chart_type, commodity_chart = create_trend_chart(df_commodity, "Komoditas")
            if chart_type == "plotly":
                st.plotly_chart(commodity_chart, use_container_width=True)
            else:
                st.write("### Tren Ekspor Berdasarkan Komoditas")
                st.line_chart(commodity_chart)
                
        with col2:
            chart_type, country_chart = create_trend_chart(df_country, "Negara")
            if chart_type == "plotly":
                st.plotly_chart(country_chart, use_container_width=True)
            else:
                st.write("### Tren Ekspor Berdasarkan Negara")
                st.line_chart(country_chart)

        st.header("🗺️ Distribusi Ekspor Global")
        world_map = create_choropleth_map(df_country, selected_year)
        if world_map:
            st.plotly_chart(world_map, use_container_width=True)

    elif analysis_type == "Analisis Komoditas":
        st.header("🏭 Analisis Ekspor Komoditas")
        top_n = st.sidebar.slider("Jumlah Komoditas Teratas", 5, 20, 10)
        current_year_col = f'export_value_{selected_year}'

        st.subheader(f'{top_n} Komoditas Ekspor Teratas ({selected_year})')
        chart_type, top_items_fig = create_top_items_chart(df_commodity, current_year_col, 'description', f'Top {top_n} Commodities ({selected_year})', top_n)
        if chart_type == "plotly":
            st.plotly_chart(top_items_fig, use_container_width=True)
        else:
            st.bar_chart(top_items_fig)
        
        chart_type, pie_fig = create_pie_chart(df_commodity, current_year_col, 'description', f'Pangsa Pasar {top_n} Komoditas Teratas ({selected_year})', top_n)
        if chart_type == "plotly":
            st.plotly_chart(pie_fig, use_container_width=True)
        else:
            st.pyplot(pie_fig)

    elif analysis_type == "Analisis Negara":
        st.header("🌍 Analisis Ekspor Berdasarkan Negara Tujuan")
        top_n = st.sidebar.slider("Jumlah Negara Teratas", 5, 20, 10)
        current_year_col = f'export_value_{selected_year}'

        st.subheader(f'{top_n} Negara Tujuan Ekspor Teratas ({selected_year})')
        chart_type, top_items_fig = create_top_items_chart(df_country, current_year_col, 'country', f'Top {top_n} Countries ({selected_year})', top_n)
        if chart_type == "plotly":
            st.plotly_chart(top_items_fig, use_container_width=True)
        else:
            st.bar_chart(top_items_fig)

        chart_type, pie_fig = create_pie_chart(df_country, current_year_col, 'country', f'Pangsa Pasar {top_n} Negara Teratas ({selected_year})', top_n)
        if chart_type == "plotly":
            st.plotly_chart(pie_fig, use_container_width=True)
        else:
            st.pyplot(pie_fig)

if __name__ == "__main__":
    main()
