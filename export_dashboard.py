import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pycountry
import numpy as np

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

def get_iso_a3(country_name):
    """Convert country name to ISO Alpha-3 code"""
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

def create_trend_chart(data, data_type="commodity"):
    """Create trend chart for export values over years"""
    years = [2020, 2021, 2022, 2023, 2024]
    year_columns = [f'export_value_{year}' for year in years]
    
    # Calculate total exports per year
    total_exports = []
    for col in year_columns:
        if col in data.columns:
            total_exports.append(data[col].sum())
        else:
            total_exports.append(0)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years,
        y=total_exports,
        mode='lines+markers',
        name=f'Total Export Value ({data_type.title()})',
        line=dict(width=3, color='#1f77b4'),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f'Export Trend Over Time - {data_type.title()}',
        xaxis_title='Year',
        yaxis_title='Export Value (USD)',
        hovermode='x unified',
        showlegend=False
    )
    
    return fig

def create_top_items_chart(data, value_col, label_col, title, top_n=10):
    """Create horizontal bar chart for top items"""
    top_data = data.nlargest(top_n, value_col)
    
    fig = px.bar(
        top_data,
        x=value_col,
        y=label_col,
        orientation='h',
        title=title,
        color=value_col,
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        height=500
    )
    
    return fig

def create_pie_chart(data, values_col, names_col, title, top_n=10):
    """Create pie chart for distribution"""
    top_data = data.nlargest(top_n, values_col)
    
    fig = px.pie(
        top_data,
        values=values_col,
        names=names_col,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def create_world_map(df_country):
    """Create world map visualization"""
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
        ["Overview", "Commodity Analysis", "Country Analysis", "Comparative Analysis"]
    )
    
    # Additional filters based on analysis type
    if analysis_type == "Commodity Analysis":
        top_n_commodities = st.sidebar.slider("Number of Top Commodities", 5, 20, 10)
        commodity_filter = st.sidebar.multiselect(
            "Filter by Commodity",
            options=df_commodity['description'].unique()[:20],
            default=[]
        )
    elif analysis_type == "Country Analysis":
        top_n_countries = st.sidebar.slider("Number of Top Countries", 5, 20, 10)
        country_filter = st.sidebar.multiselect(
            "Filter by Country",
            options=df_country['country'].unique()[:20],
            default=[]
        )
    
    # Main content based on analysis type
    if analysis_type == "Overview":
        st.header("📈 Export Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        current_year_col = f'export_value_{selected_year}'
        
        with col1:
            total_commodity_export = df_commodity[current_year_col].sum() if current_year_col in df_commodity.columns else 0
            st.metric(
                "Total Commodity Export",
                f"${total_commodity_export:,.0f}M",
                delta=None
            )
        
        with col2:
            total_country_export = df_country[current_year_col].sum() if current_year_col in df_country.columns else 0
            st.metric(
                "Total Country Export",
                f"${total_country_export:,.0f}M",
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
            commodity_trend = create_trend_chart(df_commodity, "commodity")
            st.plotly_chart(commodity_trend, use_container_width=True)
        
        with col2:
            country_trend = create_trend_chart(df_country, "country")
            st.plotly_chart(country_trend, use_container_width=True)
        
        # World map
        st.header("🗺️ Global Export Distribution")
        world_map = create_world_map(df_country)
        st.plotly_chart(world_map, use_container_width=True)
    
    elif analysis_type == "Commodity Analysis":
        st.header("🏭 Commodity Export Analysis")
        
        # Filter data if needed
        filtered_df = df_commodity.copy()
        if commodity_filter:
            filtered_df = filtered_df[filtered_df['description'].isin(commodity_filter)]
        
        current_year_col = f'export_value_{selected_year}'
        
        # Top commodities chart
        if current_year_col in filtered_df.columns:
            top_commodities_chart = create_top_items_chart(
                filtered_df,
                current_year_col,
                'description',
                f'Top {top_n_commodities} Commodities Export ({selected_year})',
                top_n_commodities
            )
            st.plotly_chart(top_commodities_chart, use_container_width=True)
            
            # Pie chart
            col1, col2 = st.columns(2)
            
            with col1:
                pie_chart = create_pie_chart(
                    filtered_df,
                    current_year_col,
                    'description',
                    f'Export Distribution by Commodity ({selected_year})',
                    top_n_commodities
                )
                st.plotly_chart(pie_chart, use_container_width=True)
            
            with col2:
                # Data table
                st.subheader(f"Top {top_n_commodities} Commodities Data")
                top_data = filtered_df.nlargest(top_n_commodities, current_year_col)[
                    ['description', current_year_col, 'role_percentage_2024']
                ].round(2)
                st.dataframe(top_data, use_container_width=True)
    
    elif analysis_type == "Country Analysis":
        st.header("🌍 Country Export Analysis")
        
        # Filter data if needed
        filtered_df = df_country.copy()
        if country_filter:
            filtered_df = filtered_df[filtered_df['country'].isin(country_filter)]
        
        current_year_col = f'export_value_{selected_year}'
        
        # Top countries chart
        if current_year_col in filtered_df.columns:
            top_countries_chart = create_top_items_chart(
                filtered_df,
                current_year_col,
                'country',
                f'Top {top_n_countries} Export Destinations ({selected_year})',
                top_n_countries
            )
            st.plotly_chart(top_countries_chart, use_container_width=True)
            
            # Pie chart and world map
            col1, col2 = st.columns(2)
            
            with col1:
                pie_chart = create_pie_chart(
                    filtered_df,
                    current_year_col,
                    'country',
                    f'Export Distribution by Country ({selected_year})',
                    top_n_countries
                )
                st.plotly_chart(pie_chart, use_container_width=True)
            
            with col2:
                # Data table
                st.subheader(f"Top {top_n_countries} Countries Data")
                top_data = filtered_df.nlargest(top_n_countries, current_year_col)[
                    ['country', current_year_col, 'role_percentage_2024']
                ].round(2)
                st.dataframe(top_data, use_container_width=True)
    
    elif analysis_type == "Comparative Analysis":
        st.header("⚖️ Comparative Analysis")
        
        # Year comparison
        st.subheader("Year-over-Year Comparison")
        
        if selected_year > 2020:
            prev_year = selected_year - 1
            current_col = f'export_value_{selected_year}'
            prev_col = f'export_value_{prev_year}'
            
            col1, col2 = st.columns(2)
            
            with col1:
                if current_col in df_commodity.columns and prev_col in df_commodity.columns:
                    current_total = df_commodity[current_col].sum()
                    prev_total = df_commodity[prev_col].sum()
                    change = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
                    
                    st.metric(
                        f"Commodity Export ({selected_year})",
                        f"${current_total:,.0f}M",
                        f"{change:+.1f}% vs {prev_year}"
                    )
            
            with col2:
                if current_col in df_country.columns and prev_col in df_country.columns:
                    current_total = df_country[current_col].sum()
                    prev_total = df_country[prev_col].sum()
                    change = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
                    
                    st.metric(
                        f"Country Export ({selected_year})",
                        f"${current_total:,.0f}M",
                        f"{change:+.1f}% vs {prev_year}"
                    )
        
        # Top performers comparison
        st.subheader("Top Performers Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top 5 Commodities**")
            if f'export_value_{selected_year}' in df_commodity.columns:
                top_commodities = df_commodity.nlargest(5, f'export_value_{selected_year}')[
                    ['description', f'export_value_{selected_year}']
                ]
                st.dataframe(top_commodities, use_container_width=True)
        
        with col2:
            st.write("**Top 5 Countries**")
            if f'export_value_{selected_year}' in df_country.columns:
                top_countries = df_country.nlargest(5, f'export_value_{selected_year}')[
                    ['country', f'export_value_{selected_year}']
                ]
                st.dataframe(top_countries, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "📊 **Indonesia Non-Oil Export Dashboard** | "
        "Data source: Ministry of Trade, Republic of Indonesia | "
        "Built with Streamlit & Plotly"
    )

if __name__ == "__main__":
    main()
