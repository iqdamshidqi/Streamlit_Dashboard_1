import streamlit as st
import pandas as pd
import numpy as np

# Check for optional dependencies
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Indonesia Non-Oil Export Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
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
    .chart-container {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the export data"""
    try:
        # Load commodity data
        df_commodity = pd.read_csv('ekspor_non_migas_komoditi.csv')
        # Remove redundant header if exists
        if df_commodity.iloc[0].astype(str).str.contains('HS|URAIAN').any():
            df_commodity = df_commodity.iloc[1:].copy()
        
        # Rename commodity columns
        commodity_columns = {
            'HS': 'hs_code',
            'URAIAN': 'description',
            '2020': 'export_value_2020',
            '2021': 'export_value_2021',
            '2022': 'export_value_2022',
            '2023': 'export_value_2023',
            '2024': 'export_value_2024',
            'Trend (%)  2020 -  2024': 'trend_percentage_2020_2024',
            'Perub (%)  2024 -  2023': 'change_percentage_2024_2023',
            'Peran (%)  2024': 'role_percentage_2024',
            'Jan-Mei': 'export_value_jan_may_2024',
            'Jan-Mei.1': 'export_value_jan_may_2025',
            'Perub (%)  2025/  2024': 'change_percentage_jan_may_2025_2024',
            'Peran (%)  2025': 'role_percentage_2025'
        }
        df_commodity.rename(columns=commodity_columns, inplace=True)
        
        # Load country data
        df_country = pd.read_csv('ekspor_non_migas_negara_english.csv')
        
        # Rename country columns
        country_columns = {
            'COUNTRY': 'country',
            '2020': 'export_value_2020',
            '2021': 'export_value_2021',
            '2022': 'export_value_2022',
            '2023': 'export_value_2023',
            '2024': 'export_value_2024',
            'Trend (%) 2020 -  2024': 'trend_percentage_2020_2024',
            'Perub (%) 2024 -  2023': 'change_percentage_2024_2023',
            'Peran (%) 2024': 'role_percentage_2024',
            'Jan-Mei': 'export_value_jan_may_2024',
            'Jan-Mei.1': 'export_value_jan_may_2025',
            'Perub (%) 2025/  2024': 'change_percentage_jan_may_2025_2024',
            'Peran (%) 2025': 'role_percentage_2025'
        }
        df_country.rename(columns=country_columns, inplace=True)
        
        # Convert numeric columns
        numeric_cols = [col for col in df_commodity.columns if 'export_value' in col or 'percentage' in col]
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
    """Create bar chart using Streamlit's native chart functions"""
    top_data = data.nlargest(top_n, value_col).copy()
    top_data = top_data.set_index(label_col)
    
    st.subheader(title)
    st.bar_chart(top_data[value_col])
    
    return top_data

def create_streamlit_line_chart(data, data_type="commodity"):
    """Create line chart using Streamlit's native chart functions"""
    years = [2020, 2021, 2022, 2023, 2024]
    year_columns = [f'export_value_{year}' for year in years]
    
    # Calculate total exports per year
    trend_data = {}
    for i, col in enumerate(year_columns):
        if col in data.columns:
            trend_data[years[i]] = data[col].sum()
        else:
            trend_data[years[i]] = 0
    
    trend_df = pd.DataFrame(list(trend_data.items()), columns=['Year', 'Export_Value'])
    
    # -- TAMBAHKAN BARIS INI --
    # Ubah tipe data kolom 'Year' menjadi string untuk format yang benar
    trend_df['Year'] = trend_df['Year'].astype(str)
    
    trend_df = trend_df.set_index('Year')
    
    st.subheader(f'Export Trend Over Time - {data_type.title()}')
    st.line_chart(trend_df)
    
    return trend_df

def get_iso_a3(country_name):
    """Convert country name to ISO Alpha-3 code"""
    if not PYCOUNTRY_AVAILABLE:
        return None
        
    country_mapping = {
        'REPUBLIC OF CHINA': 'CHN',
        'UNITED STATES': 'USA',
        'SOUTH KOREA': 'KOR',
        'UNITED KINGDOM': 'GBR',
        'RUSSIAN FEDERATION': 'RUS',
        'CZECH REPUBLIC': 'CZE',
        'BOLIVIA': 'BOL',
        'VENEZUELA': 'VEN',
        'IRAN': 'IRN',
        "LAO PEOPLE'S DEMOCRATIC REPUBLIC": 'LAO',
        'MOLDOVA': 'MDA',
        'SYRIA': 'SYR',
        'TANZANIA': 'TZA',
        'VIETNAM': 'VNM',
        'BRUNEI DARUSSALAM': 'BRN',
        'CABO VERDE': 'CPV',
        'CONGO': 'COG',
        'DEMOCRATIC REPUBLIC OF THE CONGO': 'COD',
        'EGYPT': 'EGY',
        'GAMBIA': 'GMB',
        'GUINEA BISSAU': 'GNB',
        'SAO TOME AND PRINCIPE': 'STP',
        'SWAZILAND': 'SWZ',
        'UNITED ARAB EMIRATES': 'ARE',
        'YEMEN': 'YEM',
        'NORTH MACEDONIA': 'MKD',
        'PALESTINE': 'PSE',
        "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF": 'PRK'
    }
    
    if country_name in country_mapping:
        return country_mapping[country_name]
    
    try:
        return pycountry.countries.search_fuzzy(country_name)[0].alpha_3
    except LookupError:
        return None

def create_data_table(data, value_col, label_col, title, top_n=10):
    """Create formatted data table"""
    top_data = data.nlargest(top_n, value_col)
    
    # Format the data for display
    display_data = top_data[[label_col, value_col]].copy()
    display_data[value_col] = display_data[value_col].apply(lambda x: f"${x:,.0f}M")
    display_data.columns = [label_col.replace('_', ' ').title(), 'Export Value']
    
    st.subheader(title)
    st.dataframe(display_data, use_container_width=True)
    
    return display_data

def format_number(num):
    """Format large numbers with appropriate suffixes"""
    if num >= 1e9:
        return f"${num/1e9:.1f}B"
    elif num >= 1e6:
        return f"${num/1e6:.1f}M"
    elif num >= 1e3:
        return f"${num/1e3:.1f}K"
    else:
        return f"${num:.0f}"

def calculate_growth_rate(current, previous):
    """Calculate growth rate between two periods"""
    if previous == 0 or pd.isna(previous) or pd.isna(current):
        return 0
    return ((current - previous) / previous) * 100

def create_world_map(df_country):
    """Create world map visualization"""
    if not PLOTLY_AVAILABLE or not PYCOUNTRY_AVAILABLE:
        st.warning("World map requires plotly and pycountry libraries")
        return None
        
    # Add ISO codes
    df_country['iso_a3'] = df_country['country'].apply(get_iso_a3)
    df_map = df_country.dropna(subset=['iso_a3'])
    
    fig = px.choropleth(
        df_map,
        locations="iso_a3",
        color="export_value_2024",
        hover_name="country",
        hover_data={"export_value_2024": ":,.0f"},
        color_continuous_scale="plasma",
        title="Export Distribution by Country (2024)"
    )
    
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True),
        height=500
    )
    
    return fig

def create_donut_chart_with_total(data, values_col, names_col, title, top_n=10):
    """Membuat donut chart dengan total nilai di tengah."""
    if data.empty or values_col not in data.columns:
        st.warning("Data tidak tersedia untuk membuat chart.")
        return None

    # Ambil data teratas dan hitung totalnya
    top_data = data.nlargest(top_n, values_col)
    total_value = top_data[values_col].sum()
    formatted_total = format_number(total_value) # Menggunakan fungsi format_number yang sudah ada

    # Buat donut chart menggunakan Plotly Express
    fig = px.pie(
        top_data,
        values=values_col,
        names=names_col,
        title=title,
        hole=0.4,  # Ini yang membuat chart menjadi donut
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # Atur agar label persentase berada di luar slice untuk keterbacaan
    fig.update_traces(textposition='outside', textinfo='percent+label', pull=[0.02] * top_n)

    # Tambahkan anotasi total nilai di tengah chart
    fig.update_layout(
        showlegend=False,
        annotations=[
            dict(
                text=f"Total<br>{formatted_total}",
                x=0.5,
                y=0.5,
                font_size=22,
                showarrow=False
            )
        ]
    )
    return fig

def main():
    # Header
    st.markdown('<p class="main-header">🇮🇩 Indonesia Non-Oil Export Dashboard</p>', unsafe_allow_html=True)
    
    # Load data
    df_commodity, df_country = load_data()
    
    if df_commodity is None or df_country is None:
        st.error("Failed to load data. Please check your CSV files.")
        return
    
    # Sidebar for filters
    st.sidebar.header("🎛️ Dashboard Filters")
    
    # Year selection
    available_years = [2020, 2021, 2022, 2023, 2024]
    selected_year = st.sidebar.selectbox(
        "Select Year for Analysis",
        available_years,
        index=len(available_years)-1  # Default to latest year
    )
    
    # Analysis type selection
    analysis_type = st.sidebar.radio(
        "Select Analysis Type",
        ["📊 Overview", "🏭 Commodity Analysis", "🌍 Country Analysis", "⚖️ Comparative Analysis"]
    )
    
    # Additional filters based on analysis type
    if analysis_type == "🏭 Commodity Analysis":
        top_n_commodities = st.sidebar.slider("Number of Top Commodities", 5, 20, 10)
        commodity_filter = st.sidebar.multiselect(
            "Filter by Commodity",
            options=df_commodity['description'].unique()[:20],
            default=[]
        )
    elif analysis_type == "🌍 Country Analysis":
        top_n_countries = st.sidebar.slider("Number of Top Countries", 5, 20, 10)
        country_filter = st.sidebar.multiselect(
            "Filter by Country",
            options=df_country['country'].unique()[:20],
            default=[]
        )
    
    # Main content based on analysis type
    if analysis_type == "📊 Overview":
        st.header("📈 Export Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        current_year_col = f'export_value_{selected_year}'
        
        with col1:
            total_commodity_export = df_commodity[current_year_col].sum() if current_year_col in df_commodity.columns else 0
            st.metric(
                "Total Commodity Export",
                format_number(total_commodity_export),
                delta=None
            )
        
        with col2:
            total_country_export = df_country[current_year_col].sum() if current_year_col in df_country.columns else 0
            st.metric(
                "Total Country Export",
                format_number(total_country_export),
                delta=None
            )
        
        with col3:
            num_commodities = len(df_commodity)
            st.metric("Total Commodities", num_commodities)
        
        with col4:
            num_countries = len(df_country)
            st.metric("Export Destinations", num_countries)
        
        # Trend charts
        col1, col2 = st.columns(2)
        
        with col1:
            create_streamlit_line_chart(df_commodity, "commodity")
        
        with col2:
            create_streamlit_line_chart(df_country, "country")
        
        # Top performers overview
        st.header("🏆 Top Performers Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if current_year_col in df_commodity.columns:
                create_data_table(
                    df_commodity,
                    current_year_col,
                    'description',
                    f"Top 5 Commodities ({selected_year})",
                    5
                )
        
        with col2:
            if current_year_col in df_country.columns:
                create_data_table(
                    df_country,
                    current_year_col,
                    'country',
                    f"Top 5 Countries ({selected_year})",
                    5
                )

    # World map
        st.header("🗺️ Global Export Distribution")
        world_map = create_world_map(df_country)
        if world_map:
            if PLOTLY_AVAILABLE:
                st.plotly_chart(world_map, use_container_width=True)
            else:
                st.pyplot(world_map)
    
    # ... (potongan kode di dalam fungsi main)
    
    elif analysis_type == "🏭 Commodity Analysis":
        # TAMBAHKAN INDENTASI DI SINI
        st.header("🏭 Commodity Export Analysis")
        
        # Filter data jika dibutuhkan
        filtered_df = df_commodity.copy()
        if commodity_filter:
            filtered_df = filtered_df[filtered_df['description'].isin(commodity_filter)]
        
        current_year_col = f'export_value_{selected_year}'
        
        if current_year_col in filtered_df.columns and not filtered_df.empty:
            
            # --- BAGIAN DONUT CHART YANG BARU DITAMBAHKAN ---
            st.subheader(f"📈 Distribusi Persentase Top {top_n_commodities} Komoditas ({selected_year})")
            donut_fig = create_donut_chart_with_total(
                filtered_df,
                values_col=current_year_col,
                names_col='description',
                title=f"Pangsa Ekspor Top {top_n_commodities} Komoditas",
                top_n=top_n_commodities
            )
            if donut_fig:
                st.plotly_chart(donut_fig, use_container_width=True)
            
            st.markdown("---") # Pemisah visual
            # --- AKHIR BAGIAN BARU ---

            # Bagian Bar Chart dan Tabel Data (yang sudah ada sebelumnya)
            col1, col2 = st.columns([2, 1])
            
            with col1:
                create_streamlit_bar_chart(
                    filtered_df,
                    current_year_col,
                    'description',
                    f'Top {top_n_commodities} Komoditas Ekspor ({selected_year})',
                    top_n_commodities
                )
            
            with col2:
                # Summary statistics
                st.subheader("📊 Summary Statistics")
                total_export = filtered_df[current_year_col].sum()
                avg_export = filtered_df[current_year_col].mean()
                max_export = filtered_df[current_year_col].max()
                
                st.metric("Total Export", format_number(total_export))
                st.metric("Average Export", format_number(avg_export))
                st.metric("Highest Export", format_number(max_export))
            
            # Detailed data table (sudah ada)
            create_data_table(
                filtered_df,
                current_year_col,
                'description',
                f"Detailed Commodity Data ({selected_year})",
                top_n_commodities
            )
        else:
            st.warning(f"Tidak ada data untuk ditampilkan pada tahun {selected_year} dengan filter yang dipilih.")

    
    elif analysis_type == "🌍 Country Analysis":
        st.header("🌍 Country Export Analysis")
        
        # Filter data if needed
        filtered_df = df_country.copy()
        if country_filter:
            filtered_df = filtered_df[filtered_df['country'].isin(country_filter)]
        
        current_year_col = f'export_value_{selected_year}'
        
        # Top countries chart
        if current_year_col in filtered_df.columns:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                create_streamlit_bar_chart(
                    filtered_df,
                    current_year_col,
                    'country',
                    f'Top {top_n_countries} Export Destinations ({selected_year})',
                    top_n_countries
                )
            
            with col2:
                # Summary statistics
                st.subheader("📊 Summary Statistics")
                total_export = filtered_df[current_year_col].sum()
                avg_export = filtered_df[current_year_col].mean()
                max_export = filtered_df[current_year_col].max()
                
                st.metric("Total Export", format_number(total_export))
                st.metric("Average Export", format_number(avg_export))
                st.metric("Highest Export", format_number(max_export))
            
            # Regional analysis
            st.subheader("🗺️ Regional Distribution")
            
            # Simple regional grouping (you can expand this)
            regional_mapping = {
                'CHINA': 'Asia',
                'UNITED STATES': 'North America',
                'INDIA': 'Asia',
                'SINGAPORE': 'Asia',
                'MALAYSIA': 'Asia',
                'THAILAND': 'Asia',
                'VIETNAM': 'Asia',
                'PHILIPPINES': 'Asia',
                'SOUTH KOREA': 'Asia',
                'JAPAN': 'Asia',
                'NETHERLANDS': 'Europe',
                'GERMANY': 'Europe',
                'ITALY': 'Europe',
                'SPAIN': 'Europe',
                'FRANCE': 'Europe',
                'UNITED KINGDOM': 'Europe',
                'BRAZIL': 'South America',
                'ARGENTINA': 'South America',
                'AUSTRALIA': 'Oceania'
            }
            
            # Add region column
            filtered_df['region'] = filtered_df['country'].map(regional_mapping).fillna('Other')
            
            # Calculate regional totals
            regional_data = filtered_df.groupby('region')[current_year_col].sum().sort_values(ascending=False)
            regional_df = pd.DataFrame({'Region': regional_data.index, 'Export Value': regional_data.values})
            regional_df['Export Value Formatted'] = regional_df['Export Value'].apply(format_number)
            
            st.dataframe(regional_df[['Region', 'Export Value Formatted']], use_container_width=True)
            
            # Detailed country data
            create_data_table(
                filtered_df,
                current_year_col,
                'country',
                f"Detailed Country Data ({selected_year})",
                top_n_countries
            )
    
    elif analysis_type == "⚖️ Comparative Analysis":
        st.header("⚖️ Comparative Analysis")
        
        # Year comparison
        st.subheader("📅 Year-over-Year Comparison")
        
        if selected_year > 2020:
            prev_year = selected_year - 1
            current_col = f'export_value_{selected_year}'
            prev_col = f'export_value_{prev_year}'
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if current_col in df_commodity.columns and prev_col in df_commodity.columns:
                    current_total = df_commodity[current_col].sum()
                    prev_total = df_commodity[prev_col].sum()
                    change = calculate_growth_rate(current_total, prev_total)
                    
                    st.metric(
                        f"Commodity Export ({selected_year})",
                        format_number(current_total),
                        f"{change:+.1f}% vs {prev_year}"
                    )
            
            with col2:
                if current_col in df_country.columns and prev_col in df_country.columns:
                    current_total = df_country[current_col].sum()
                    prev_total = df_country[prev_col].sum()
                    change = calculate_growth_rate(current_total, prev_total)
                    
                    st.metric(
                        f"Country Export ({selected_year})",
                        format_number(current_total),
                        f"{change:+.1f}% vs {prev_year}"
                    )
            
            with col3:
                # Growth rate analysis
                if current_col in df_commodity.columns and prev_col in df_commodity.columns:
                    growth_commodities = df_commodity[df_commodity[current_col] > df_commodity[prev_col]]
                    st.metric("Growing Commodities", len(growth_commodities))
            
            with col4:
                # Growth rate analysis
                if current_col in df_country.columns and prev_col in df_country.columns:
                    growth_countries = df_country[df_country[current_col] > df_country[prev_col]]
                    st.metric("Growing Markets", len(growth_countries))
        
        # Top performers comparison
        st.subheader("🏆 Top Performers Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🏭 Top 10 Commodities**")
            if f'export_value_{selected_year}' in df_commodity.columns:
                top_commodities = df_commodity.nlargest(10, f'export_value_{selected_year}')[
                    ['description', f'export_value_{selected_year}']
                ].copy()
                top_commodities[f'export_value_{selected_year}'] = top_commodities[f'export_value_{selected_year}'].apply(format_number)
                top_commodities.columns = ['Commodity', 'Export Value']
                st.dataframe(top_commodities, use_container_width=True, hide_index=True)
        
        with col2:
            st.write("**🌍 Top 10 Countries**")
            if f'export_value_{selected_year}' in df_country.columns:
                top_countries = df_country.nlargest(10, f'export_value_{selected_year}')[
                    ['country', f'export_value_{selected_year}']
                ].copy()
                top_countries[f'export_value_{selected_year}'] = top_countries[f'export_value_{selected_year}'].apply(format_number)
                top_countries.columns = ['Country', 'Export Value']
                st.dataframe(top_countries, use_container_width=True, hide_index=True)
        
        # Trend comparison
        st.subheader("📈 Multi-Year Trend Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Commodity trend
            create_streamlit_line_chart(df_commodity, "Commodity")
            
            # Show trend summary
            years = [2020, 2021, 2022, 2023, 2024]
            trend_summary = []
            for year in years:
                col_name = f'export_value_{year}'
                if col_name in df_commodity.columns:
                    total = df_commodity[col_name].sum()
                    trend_summary.append({'Year': year, 'Total Export': format_number(total)})
            
            if trend_summary:
                trend_df = pd.DataFrame(trend_summary)
                st.dataframe(trend_df, use_container_width=True, hide_index=True)
        
        with col2:
            # Country trend
            create_streamlit_line_chart(df_country, "Country")
            
            # Show trend summary
            trend_summary = []
            for year in years:
                col_name = f'export_value_{year}'
                if col_name in df_country.columns:
                    total = df_country[col_name].sum()
                    trend_summary.append({'Year': year, 'Total Export': format_number(total)})
            
            if trend_summary:
                trend_df = pd.DataFrame(trend_summary)
                st.dataframe(trend_df, use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            """
            <div style='text-align: center'>
                <p><strong>📊 Indonesia Non-Oil Export Dashboard</strong></p>
                <p>Data source: Ministry of Trade, Republic of Indonesia</p>
                <p>Built with ❤️ using Streamlit</p>
            </div>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
