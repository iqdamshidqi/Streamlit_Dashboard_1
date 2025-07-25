import streamlit as st
import pandas as pd
import numpy as np

# Try to import plotly, fallback to streamlit's native charts or matplotlib
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    import matplotlib.pyplot as plt # Matplotlib still needed for pie chart
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not available, using Streamlit's native charts and Matplotlib as fallback.")

try:
    import pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False
    st.warning("pycountry not available, world map functionality will be limited.")

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
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the export data"""
    try:
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
        
        df_country = pd.read_csv('ekspor_non_migas_negara_english.csv')
        country_columns = {
            'COUNTRY': 'country', '2020': 'export_value_2020', '2021': 'export_value_2021',
            '2022': 'export_value_2022', '2023': 'export_value_2023', '2024': 'export_value_2024',
            'Trend (%) 2020 -  2024': 'trend_percentage_2020_2024', 'Perub (%) 2024 -  2023': 'change_percentage_2024_2023',
            'Peran (%) 2024': 'role_percentage_2024',
        }
        df_country.rename(columns=country_columns, inplace=True)
        
        numeric_cols = [col for col in df_commodity.columns if 'export_value' in col or 'percentage' in col]
        for col in numeric_cols:
            if col in df_commodity.columns:
                df_commodity[col] = pd.to_numeric(df_commodity[col], errors='coerce')
            if col in df_country.columns:
                df_country[col] = pd.to_numeric(df_country[col], errors='coerce')
        
        return df_commodity, df_country
    except FileNotFoundError as e:
        st.error(f"Error: {e}. Pastikan file CSV berada di direktori yang sama.")
        return None, None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def get_iso_a3(country_name):
    # This function remains the same
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
    """Create trend chart for export values over years"""
    years = [2020, 2021, 2022, 2023, 2024]
    year_columns = [f'export_value_{year}' for year in years]
    total_exports = [data[col].sum() if col in data.columns else 0 for col in year_columns]
    
    chart_data = pd.DataFrame({
        'Year': years,
        'Total Export Value': total_exports
    }).set_index('Year')

    if PLOTLY_AVAILABLE:
        fig = px.line(
            chart_data,
            y='Total Export Value',
            title=f'Export Trend Over Time - {data_type.title()}',
            markers=True
        )
        fig.update_layout(hovermode='x unified')
        return "plotly", fig
    else:
        # Fallback to Streamlit's native line chart
        return "streamlit_native", chart_data

def create_top_items_chart(data, value_col, label_col, title, top_n=10):
    """Create bar chart for top items"""
    top_data = data.nlargest(top_n, value_col).sort_values(value_col)
    
    if PLOTLY_AVAILABLE:
        fig = px.bar(
            top_data, x=value_col, y=label_col, orientation='h', title=title,
            color=value_col, color_continuous_scale='viridis'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
        return "plotly", fig
    else:
        # Fallback to Streamlit's native bar chart
        chart_data = top_data.set_index(label_col)[[value_col]]
        return "streamlit_native", chart_data

def create_pie_chart(data, values_col, names_col, title, top_n=10):
    """Create pie chart for distribution"""
    top_data = data.nlargest(top_n, values_col)
    
    if PLOTLY_AVAILABLE:
        fig = px.pie(
            top_data, values=values_col, names=names_col, title=title,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return "plotly", fig
    else:
        # Fallback to Matplotlib as Streamlit has no native pie chart
        st.subheader(title) # Add title manually since st.pyplot doesn't have one
        fig, ax = plt.subplots()
        ax.pie(top_data[values_col], labels=top_data[names_col], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        return "matplotlib", fig

def create_choropleth_map(input_df, selected_year):
    """Create world map visualization"""
    if not PLOTLY_AVAILABLE or not PYCOUNTRY_AVAILABLE:
        st.warning("World map requires Plotly and PyCountry libraries.")
        return None
        
    df_map = input_df.copy()
    df_map['iso_a3'] = df_map['country'].apply(get_iso_a3)
    df_map.dropna(subset=['iso_a3'], inplace=True)
    
    color_col = f'export_value_{selected_year}'
    
    fig = px.choropleth(
        df_map,
        locations="iso_a3",
        color=color_col,
        hover_name="country",
        hover_data={color_col: ":,.0f"},
        color_continuous_scale="plasma",
        title=f"Export Distribution by Country ({selected_year})"
    )
    fig.update_layout(geo=dict(showframe=False, showcoastlines=True))
    return fig

def main():
    st.markdown('<p class="main-header">🇮🇩 Indonesia Non-Oil Export Dashboard</p>', unsafe_allow_html=True)
    
    df_commodity, df_country = load_data()
    if df_commodity is None: return

    st.sidebar.header("🎛️ Dashboard Filters")
    available_years = [2020, 2021, 2022, 2023, 2024]
    selected_year = st.sidebar.selectbox(
        "Select Year", available_years, index=len(available_years)-1
    )
    
    analysis_type = st.sidebar.radio(
        "Select Analysis",
        ["Overview", "Commodity Analysis", "Country Analysis"]
    )
    
    # --- Main content ---
    if analysis_type == "Overview":
        st.header("📈 Export Overview")
        current_year_col = f'export_value_{selected_year}'
        
        col1, col2 = st.columns(2)
        
        # Trend Charts
        with col1:
            chart_type, commodity_chart = create_trend_chart(df_commodity, "Commodity")
            if chart_type == "plotly":
                st.plotly_chart(commodity_chart, use_container_width=True)
            else:
                st.write("### Export Trend Over Time - Commodity")
                st.line_chart(commodity_chart)
                
        with col2:
            chart_type, country_chart = create_trend_chart(df_country, "Country")
            if chart_type == "plotly":
                st.plotly_chart(country_chart, use_container_width=True)
            else:
                st.write("### Export Trend Over Time - Country")
                st.line_chart(country_chart)

        # World map
        st.header("🗺️ Global Export Distribution")
        world_map = create_choropleth_map(df_country, selected_year)
        if world_map:
            st.plotly_chart(world_map, use_container_width=True)

    elif analysis_type == "Commodity Analysis":
        st.header("🏭 Commodity Export Analysis")
        top_n = st.sidebar.slider("Number of Top Commodities", 5, 20, 10)
        current_year_col = f'export_value_{selected_year}'

        st.subheader(f'Top {top_n} Commodities Exported ({selected_year})')
        chart_type, top_items_fig = create_top_items_chart(
            df_commodity, current_year_col, 'description', f'Top {top_n} Commodities ({selected_year})', top_n
        )
        if chart_type == "plotly":
            st.plotly_chart(top_items_fig, use_container_width=True)
        else:
            st.bar_chart(top_items_fig)
        
        # Pie chart
        chart_type, pie_fig = create_pie_chart(
            df_commodity, current_year_col, 'description', f'Share of Top {top_n} Commodities ({selected_year})', top_n
        )
        if chart_type == "plotly":
            st.plotly_chart(pie_fig, use_container_width=True)
        else: # Matplotlib fallback
            st.pyplot(pie_fig)

    elif analysis_type == "Country Analysis":
        st.header("🌍 Country Export Analysis")
        top_n = st.sidebar.slider("Number of Top Countries", 5, 20, 10)
        current_year_col = f'export_value_{selected_year}'

        st.subheader(f'Top {top_n} Export Destinations ({selected_year})')
        chart_type, top_items_fig = create_top_items_chart(
            df_country, current_year_col, 'country', f'Top {top_n} Countries ({selected_year})', top_n
        )
        if chart_type == "plotly":
            st.plotly_chart(top_items_fig, use_container_width=True)
        else:
            st.bar_chart(top_items_fig)

        # Pie chart
        chart_type, pie_fig = create_pie_chart(
            df_country, current_year_col, 'country', f'Share of Top {top_n} Countries ({selected_year})', top_n
        )
        if chart_type == "plotly":
            st.plotly_chart(pie_fig, use_container_width=True)
        else: # Matplotlib fallback
            st.pyplot(pie_fig)

if __name__ == "__main__":
    main()
