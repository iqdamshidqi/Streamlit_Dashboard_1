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


# --- CSS Kustom ---
st.markdown("""
<style>
    .main-header {
        font-size: 8rem;
        font-weight: bold;
        color: #fffff;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)


# --- Fungsi-Fungsi Helper ---

@st.cache_data
def load_data():
    """Memuat dan memproses data ekspor."""
    try:
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
        st.error(f"Error loading data: {str(e)}")
        return None, None

def create_streamlit_bar_chart(data, value_col, label_col, title, top_n=10):
    """Membuat bar chart menggunakan fungsi bawaan Streamlit."""
    top_data = data.nlargest(top_n, value_col).copy()
    top_data = top_data.set_index(label_col)
    st.subheader(title)
    st.bar_chart(top_data[value_col])
    return top_data

def create_streamlit_line_chart(data, data_type="commodity"):
    """Membuat line chart menggunakan fungsi bawaan Streamlit."""
    years = [2020, 2021, 2022, 2023, 2024]
    year_columns = [f'export_value_{year}' for year in years]
    trend_data = {years[i]: data[col].sum() if col in data.columns else 0 for i, col in enumerate(year_columns)}
    trend_df = pd.DataFrame(list(trend_data.items()), columns=['Year', 'Export_Value'])
    trend_df['Year'] = trend_df['Year'].astype(str)
    trend_df = trend_df.set_index('Year')
    st.subheader(f'Export Trend Over Time - {data_type.title()}')
    st.line_chart(trend_df)
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
    """Membuat tabel data yang diformat."""
    top_data = data.nlargest(top_n, value_col)
    display_data = top_data[[label_col, value_col]].copy()
    display_data[value_col] = display_data[value_col].apply(lambda x: f"${x:,.0f}M")
    display_data.columns = [label_col.replace('_', ' ').title(), 'Export Value']
    st.subheader(title)
    st.dataframe(display_data, use_container_width=True, hide_index=True)
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
    """Membuat visualisasi peta dunia dengan highlight opsional."""
    if not PYCOUNTRY_AVAILABLE:
        st.warning("World map requires pycountry library")
        return None
    df_country['iso_a3'] = df_country['country'].apply(get_iso_a3)
    df_map = df_country.dropna(subset=['iso_a3'])
    color_col = f"export_value_{year}"
    if color_col not in df_map.columns:
        st.warning(f"Data for year {year} not available for the map.")
        return None
    fig = px.choropleth(
        df_map, locations="iso_a3", color=color_col, hover_name="country",
        hover_data={color_col: ":,.0f"}, color_continuous_scale="Plasma",
        title=f"Export Distribution by Country ({year})"
    )
    if highlighted_countries:
        highlight_df = df_map[df_map['country'].isin(highlighted_countries)]
        if not highlight_df.empty:
            fig.add_trace(go.Scattergeo(
                locations=highlight_df['iso_a3'], mode='markers',
                marker=dict(size=12, color='red', line=dict(width=2, color='white')),
                hoverinfo='text', text=highlight_df['country'], name='Pilihan Negara'
            ))
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True), height=500,
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.5)')
    )
    return fig

def create_donut_chart_with_total(data, values_col, names_col, title, top_n=10):
    """Membuat donut chart dengan total nilai di tengah."""
    if data.empty or values_col not in data.columns:
        st.warning("Data tidak tersedia untuk membuat chart.")
        return None
    top_data = data.nlargest(top_n, values_col)
    total_value = top_data[values_col].sum()
    formatted_total = format_number(total_value)
    fig = px.pie(
        top_data, values=values_col, names=names_col, title=title,
        hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition='outside', textinfo='percent+label', pull=[0.02] * top_n)
    fig.update_layout(
        showlegend=False,
        annotations=[dict(text=f"Total<br>{formatted_total}", x=0.5, y=0.5, font_size=22, showarrow=False)]
    )
    return fig


# --- Aplikasi Utama ---

def main():
    st.markdown('<p class="main-header">Indonesia Non-Oil Export Dashboard</p>', unsafe_allow_html=True)

    df_commodity, df_country = load_data()
    if df_commodity is None or df_country is None:
        return

    st.sidebar.header("🎛️ Dashboard Filters")
    available_years = [2020, 2021, 2022, 2023, 2024]
    selected_year = st.sidebar.selectbox("Select Year", available_years, index=len(available_years)-1)
    analysis_type = st.sidebar.radio(
        "Select Analysis Type",
        ["📊 Overview", "🏭 Commodity Analysis", "🌍 Country Analysis", "⚖️ Comparative Analysis"]
    )

    if analysis_type == "🏭 Commodity Analysis":
        top_n_commodities = st.sidebar.slider("Number of Top Commodities", 5, 20, 10)
        commodity_filter = st.sidebar.multiselect(
            "Filter by Commodity", options=df_commodity['description'].unique(), default=[]
        )
    elif analysis_type == "🌍 Country Analysis":
        top_n_countries = st.sidebar.slider("Number of Top Countries", 5, 20, 10)
        country_filter = st.sidebar.multiselect(
            "Filter by Country", options=df_country['country'].unique(), default=[]
        )

    current_year_col = f'export_value_{selected_year}'

    if analysis_type == "📊 Overview":
        st.header("📈 Export Overview")
        # Bagian Metrik Utama (tidak berubah)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Commodity Export", format_number(df_commodity[current_year_col].sum()))
        col2.metric("Total Country Export", format_number(df_country[current_year_col].sum()))
        col3.metric("Total Commodities", len(df_commodity))
        col4.metric("Export Destinations", len(df_country))
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            create_streamlit_line_chart(df_commodity, "Commodity")
        with col2:
            create_streamlit_line_chart(df_country, "Country")
        st.markdown("---")

        st.header(f"🏆 Top 10 Contributors in {selected_year}")
        col1, col2 = st.columns(2)

        with col1:
            commodity_donut = create_donut_chart_with_total(
                df_commodity,
                current_year_col,
                'description',
                "Commodity Distribution",
                top_n=10
            )
            if commodity_donut:
                st.plotly_chart(commodity_donut, use_container_width=True)
        
        with col2:
            country_donut = create_donut_chart_with_total(
                df_country,
                current_year_col,
                'country',
                "Country Distribution",
                top_n=10
            )
            if country_donut:
                st.plotly_chart(country_donut, use_container_width=True)
        st.markdown("---")
        
        st.header(f"🗺️ Global Export Distribution ({selected_year})")
        world_map = create_world_map(df_country, selected_year)
        if world_map:
            st.plotly_chart(world_map, use_container_width=True)

    elif analysis_type == "🏭 Commodity Analysis":
        st.header("🏭 Commodity Export Analysis")
        filtered_df = df_commodity.copy()
        if commodity_filter:
            filtered_df = filtered_df[filtered_df['description'].isin(commodity_filter)]

        if current_year_col in filtered_df.columns and not filtered_df.empty:
            st.subheader(f"📈 Distribusi Persentase Top {top_n_commodities} Komoditas ({selected_year})")
            donut_fig = create_donut_chart_with_total(
                filtered_df, current_year_col, 'description',
                f"Pangsa Ekspor Top {top_n_commodities} Komoditas", top_n_commodities
            )
            if donut_fig:
                st.plotly_chart(donut_fig, use_container_width=True)
            st.markdown("---")

            col1, col2 = st.columns([2, 1])
            with col1:
                create_streamlit_bar_chart(
                    filtered_df, current_year_col, 'description',
                    f'Top {top_n_commodities} Komoditas Ekspor ({selected_year})', top_n_commodities
                )
            with col2:
                st.subheader("📊 Ringkasan Statistik")
                total_export = filtered_df[current_year_col].sum()
                avg_export = filtered_df[current_year_col].mean()
                max_export = filtered_df[current_year_col].max()
                st.metric("Total Export", format_number(total_export))
                st.metric("Average Export", format_number(avg_export))
                st.metric("Highest Export", format_number(max_export))
                
            create_data_table(
                filtered_df, current_year_col, 'description',
                f"Data Detail Komoditas ({selected_year})", top_n_commodities
            )
        else:
            st.warning("Tidak ada data untuk ditampilkan dengan filter yang dipilih.")

    elif analysis_type == "🌍 Country Analysis":
        st.header("🌍 Country Export Analysis")
        filtered_df = df_country.copy()
        if country_filter:
            filtered_df = filtered_df[filtered_df['country'].isin(country_filter)]
            
        if current_year_col in df_country.columns and not df_country.empty:
            st.subheader(f"📈 Distribusi Persentase Top {top_n_countries} Negara Tujuan ({selected_year})")
            donut_fig = create_donut_chart_with_total(
                filtered_df, current_year_col, 'country',
                f"Pangsa Ekspor Top {top_n_countries} Negara Tujuan", top_n_countries
            )
            if donut_fig:
                st.plotly_chart(donut_fig, use_container_width=True)
            st.markdown("---")

            st.subheader(f"🗺️ Peta Distribusi Ekspor Global ({selected_year})")
            world_map_fig = create_world_map(df_country, selected_year, highlighted_countries=country_filter)
            if world_map_fig:
                st.plotly_chart(world_map_fig, use_container_width=True)
            st.markdown("---")

            col1, col2 = st.columns([2, 1])
            with col1:
                create_streamlit_bar_chart(
                    filtered_df, current_year_col, 'country',
                    f'Top {top_n_countries} Negara Tujuan ({selected_year})', top_n_countries
                )
            with col2:
                st.subheader("📊 Ringkasan Statistik")
                total_export = filtered_df[current_year_col].sum()
                avg_export = filtered_df[current_year_col].mean()
                max_export = filtered_df[current_year_col].max()
                st.metric("Total Export", format_number(total_export))
                st.metric("Average Export", format_number(avg_export))
                st.metric("Highest Export", format_number(max_export))

            create_data_table(
                filtered_df, current_year_col, 'country',
                f"Data Detail Negara ({selected_year})", top_n_countries
            )
        else:
            st.warning("Tidak ada data untuk ditampilkan dengan filter yang dipilih.")

    elif analysis_type == "⚖️ Comparative Analysis":
        st.header("⚖️ Comparative Analysis")
        if selected_year > 2020:
            prev_year = selected_year - 1
            prev_col = f'export_value_{prev_year}'
            col1, col2, col3, col4 = st.columns(4)
            current_total_comm = df_commodity[current_year_col].sum()
            prev_total_comm = df_commodity[prev_col].sum()
            col1.metric(f"Commodity Export ({selected_year})", format_number(current_total_comm),
                        f"{calculate_growth_rate(current_total_comm, prev_total_comm):+.1f}% vs {prev_year}")
            
            current_total_ctry = df_country[current_year_col].sum()
            prev_total_ctry = df_country[prev_col].sum()
            col2.metric(f"Country Export ({selected_year})", format_number(current_total_ctry),
                        f"{calculate_growth_rate(current_total_ctry, prev_total_ctry):+.1f}% vs {prev_year}")

            col3.metric("Growing Commodities", len(df_commodity[df_commodity[current_year_col] > df_commodity[prev_col]]))
            col4.metric("Growing Markets", len(df_country[df_country[current_year_col] > df_country[prev_col]]))
        else:
            st.info("Pilih tahun setelah 2020 untuk melihat perbandingan tahunan.")
        
        st.markdown("---")
        st.subheader("📈 Multi-Year Trend Comparison")
        col1, col2 = st.columns(2)
        with col1:
            create_streamlit_line_chart(df_commodity, "Commodity")
        with col2:
            create_streamlit_line_chart(df_country, "Country")

    # --- Footer ---
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p><strong>📊 Indonesia Non-Oil Export Dashboard</strong></p>
            <p>Data source: satudata.kemendag.go.id</p>
            <p>Built by: Iqdam Shidqi</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
