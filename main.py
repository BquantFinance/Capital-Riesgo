import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page config with dark theme
st.set_page_config(
    page_title="Dashboard de Entidades de Capital Riesgo Españolas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful dark theme
st.markdown("""
<style>
    /* Dark theme colors */
    :root {
        --background-primary: #0e1117;
        --background-secondary: #1a1d25;
        --background-card: #1e2128;
        --text-primary: #e6e9ef;
        --text-secondary: #8b92a8;
        --accent-primary: #7c3aed;
        --accent-secondary: #06b6d4;
        --accent-success: #10b981;
        --accent-warning: #f59e0b;
        --accent-danger: #ef4444;
        --border-color: #2a2e39;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1d25 100%);
    }
    
    /* Headers styling */
    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    h1 {
        background: linear-gradient(135deg, #06b6d4 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        margin-bottom: 1.5rem;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2128 0%, #252932 100%);
        border: 1px solid #2a2e39;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(6, 182, 212, 0.15);
        border-color: #06b6d4;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d25 0%, #0e1117 100%);
        border-right: 1px solid #2a2e39;
    }
    
    /* Dataframe styling */
    .stDataFrame > div > div {
        background-color: #1e2128 !important;
        border: 1px solid #2a2e39;
        border-radius: 8px;
    }
    
    /* Select boxes and inputs */
    .stSelectbox > div > div, .stTextInput > div > div > input {
        background-color: #1e2128 !important;
        border: 1px solid #2a2e39 !important;
        color: #e6e9ef !important;
        border-radius: 8px;
    }
    
    .stSelectbox > div > div:hover, .stTextInput > div > div > input:hover {
        border-color: #06b6d4 !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e2128;
        border: 1px solid #2a2e39;
        border-radius: 8px;
        color: #8b92a8;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #252932;
        border-color: #06b6d4;
        color: #e6e9ef;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #1e2128;
        border: 1px solid #2a2e39;
        border-radius: 8px;
        color: #e6e9ef;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1e2128;
        border: 1px solid #2a2e39;
        border-radius: 8px;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #06b6d4;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1d25;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #7c3aed 0%, #06b6d4 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #06b6d4 0%, #10b981 100%);
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('all_entities_detailed.csv')
    
    # Exclude entity types with many None values
    exclude_types = [
        'Gestora de entidades de inversión de tipo cerrado',
        'Fondo de inversión a largo plazo europeo'
    ]
    df = df[~df['entity_type'].isin(exclude_types)]
    
    # Convert date columns
    date_cols = ['fecha_registro', 'fecha_ultimo_folleto']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
    return df

# Entity type descriptions
ENTITY_DESCRIPTIONS = {
    'Fondos de capital-riesgo': 'Vehículos de inversión colectiva que invierten principalmente en empresas no cotizadas con alto potencial de crecimiento.',
    'Fondos de capital-riesgo pyme': 'Fondos especializados en inversión en pequeñas y medianas empresas (PYMEs) españolas.',
    'Fondos de capital-riesgo europeo': 'Fondos regulados a nivel europeo (EuVECA) para facilitar la inversión transfronteriza en capital riesgo.',
    'Fondos de emprendimiento social europeo': 'Fondos enfocados en empresas sociales que buscan impacto social positivo además de rentabilidad (EuSEF).',
    'Fondos de inversión colectiva de tipo cerrado': 'Fondos con un número fijo de participaciones que no permiten reembolsos hasta su vencimiento.',
    'Sociedades de capital-riesgo': 'Sociedades anónimas que realizan inversiones temporales en el capital de empresas no financieras.',
    'Sociedad de capital-riesgo pyme': 'Sociedades especializadas en inversión en PYMEs con condiciones regulatorias específicas.',
    'Sociedades de inversión colectiva de tipo cerrado': 'Sociedades de inversión con capital fijo y sin derecho de reembolso hasta el vencimiento.'
}

# Load the data
df = load_data()

# Title with gradient
st.markdown('<h1>Dashboard de Entidades de Capital Riesgo Españolas</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #8b92a8; font-size: 1.1rem; margin-top: -1rem;">Análisis de Fondos y Sociedades de Capital Riesgo e Inversión Colectiva</p>', unsafe_allow_html=True)

# Attribution and viewing requirements
col1, col2, col3 = st.columns([1.5, 1, 1])
with col1:
    st.warning('⚠️ **Recomendado**: Visualizar en **modo oscuro** y **resolución de PC** para una experiencia óptima')
with col2:
    st.markdown('<p style="text-align: right; color: #06b6d4; font-size: 0.9rem; margin-top: 0.5rem;">Desarrollado por <a href="https://twitter.com/Gsnchez" target="_blank" style="color: #06b6d4;">@Gsnchez</a></p>', unsafe_allow_html=True)
with col3:
    st.markdown('<p style="text-align: left; color: #10b981; font-size: 0.9rem; margin-top: 0.5rem;"><a href="https://bquantfinance.com" target="_blank" style="color: #10b981;">bquantfinance.com</a></p>', unsafe_allow_html=True)

# Information box
with st.expander("ℹ️ **Acerca de este Dashboard**"):
    st.markdown("""
    Este dashboard analiza las entidades de capital riesgo y vehículos de inversión colectiva registrados en España. 
    
    **Tipos de datos incluidos:**
    - **Registro oficial**: Número de registro único asignado a cada entidad
    - **Información de gestoras**: Sociedades gestoras autorizadas para administrar los fondos
    - **Entidades depositarias**: Instituciones financieras que custodian los activos
    - **Códigos ISIN**: Identificadores internacionales de valores
    - **Fechas de registro y folletos**: Información temporal sobre autorizaciones y actualizaciones
    
    El dataset se centra principalmente en vehículos de capital riesgo (FCR, SCR), incluyendo variantes especializadas en PYMEs y fondos europeos regulados (EuVECA, EuSEF).
    """)

# Sidebar filters
with st.sidebar:
    st.markdown('<h3 style="color: #06b6d4;">🔍 Filtros</h3>', unsafe_allow_html=True)
    
    # Entity type filter
    entity_types = ['Todos'] + sorted(df['entity_type'].unique().tolist())
    selected_entity = st.selectbox(
        "Tipo de Entidad",
        entity_types,
        help="Filtrar por tipo de entidad de capital riesgo o inversión colectiva"
    )
    
    # Show description if specific entity is selected
    if selected_entity != 'Todos' and selected_entity in ENTITY_DESCRIPTIONS:
        st.info(f"**{selected_entity}**: {ENTITY_DESCRIPTIONS[selected_entity]}")
    
    # Management company filter
    if selected_entity != 'Todos':
        filtered_df = df[df['entity_type'] == selected_entity]
    else:
        filtered_df = df.copy()
    
    gestoras = ['Todas'] + sorted([g for g in filtered_df['gestora_nombre'].dropna().unique()])
    selected_gestora = st.selectbox(
        "Sociedad Gestora",
        gestoras,
        help="Filtrar por sociedad gestora"
    )
    
    # Depository filter
    depositarias = ['Todas'] + sorted([d for d in filtered_df['depositaria_nombre'].dropna().unique()])
    selected_depositaria = st.selectbox(
        "Entidad Depositaria",
        depositarias,
        help="Filtrar por entidad depositaria"
    )
    
    # Date range filter
    st.markdown('<h4 style="color: #10b981; margin-top: 1rem;">📅 Rango de Fechas</h4>', unsafe_allow_html=True)
    min_date = df['fecha_registro'].min()
    max_date = df['fecha_registro'].max()
    date_range = st.date_input(
        "Fecha de Registro",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY"
    )
    
    # Add attribution at the bottom of sidebar
    st.markdown("---")
    st.markdown(
        '<div style="padding: 1rem; background: linear-gradient(135deg, #7c3aed20 0%, #06b6d420 100%); border-radius: 8px; border: 1px solid #7c3aed50;">'
        '<p style="color: #e6e9ef; font-size: 0.85rem; margin: 0;">💼 <b>Desarrollado por:</b></p>'
        '<p style="margin: 0.5rem 0;"><a href="https://twitter.com/Gsnchez" target="_blank" style="color: #06b6d4; text-decoration: none; font-weight: 600;">🐦 @Gsnchez</a></p>'
        '<p style="margin: 0;"><a href="https://bquantfinance.com" target="_blank" style="color: #10b981; text-decoration: none; font-weight: 600;">🌐 bquantfinance.com</a></p>'
        '</div>',
        unsafe_allow_html=True
    )

# Apply filters
filtered_df = df.copy()
if selected_entity != 'Todos':
    filtered_df = filtered_df[filtered_df['entity_type'] == selected_entity]
if selected_gestora != 'Todas':
    filtered_df = filtered_df[filtered_df['gestora_nombre'] == selected_gestora]
if selected_depositaria != 'Todas':
    filtered_df = filtered_df[filtered_df['depositaria_nombre'] == selected_depositaria]
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['fecha_registro'] >= pd.Timestamp(date_range[0])) &
        (filtered_df['fecha_registro'] <= pd.Timestamp(date_range[1]))
    ]

# Key metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Entidades",
        value=f"{filtered_df['entity_name'].nunique():,}",
        delta=f"{len(filtered_df):,} registros"
    )

with col2:
    st.metric(
        label="Tipos de Entidad",
        value=filtered_df['entity_type'].nunique(),
        delta="categorías"
    )

with col3:
    st.metric(
        label="Gestoras",
        value=filtered_df['gestora_nombre'].nunique(),
        delta="únicas"
    )

with col4:
    st.metric(
        label="Depositarias",
        value=filtered_df['depositaria_nombre'].nunique(),
        delta="instituciones"
    )

with col5:
    latest_date = filtered_df['fecha_registro'].max()
    st.metric(
        label="Último Registro",
        value=latest_date.strftime('%b %Y') if pd.notna(latest_date) else "N/A",
        delta="más reciente"
    )

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Análisis", "📈 Visualizaciones", "🔍 Explorador de Datos", "🏢 Empresas"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 style="color: #e6e9ef;">Distribución por Tipo de Entidad</h3>', unsafe_allow_html=True)
        entity_counts = filtered_df['entity_type'].value_counts()
        
        # Custom color palette for dark theme
        dark_theme_colors = [
            '#a855f7', '#7c3aed', '#06b6d4', '#10b981', 
            '#f59e0b', '#ef4444', '#ec4899', '#8b5cf6',
            '#3b82f6', '#14b8a6'
        ]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=entity_counts.index,
            values=entity_counts.values,
            hole=0.4,
            marker=dict(
                colors=dark_theme_colors[:len(entity_counts)],
                line=dict(color='#1a1d25', width=2)
            ),
            textfont=dict(color='white', size=12),
            hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>'
        )])
        
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6e9ef'),
            height=400,
            margin=dict(t=20, b=20),
            showlegend=True,
            legend=dict(
                font=dict(size=10),
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02
            )
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown('<h3 style="color: #e6e9ef;">Evolución Temporal de Registros</h3>', unsafe_allow_html=True)
        
        # Group by month and year
        timeline_df = filtered_df[filtered_df['fecha_registro'].notna()].copy()
        timeline_df['month_year'] = timeline_df['fecha_registro'].dt.to_period('M')
        timeline_counts = timeline_df.groupby('month_year').size().reset_index(name='count')
        timeline_counts['month_year'] = timeline_counts['month_year'].dt.to_timestamp()
        
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=timeline_counts['month_year'],
            y=timeline_counts['count'],
            mode='lines',
            fill='tozeroy',
            line=dict(color='#06b6d4', width=3),
            fillcolor='rgba(6, 182, 212, 0.15)',
            hovertemplate='<b>%{x|%b %Y}</b><br>Registros: %{y}<extra></extra>'
        ))
        
        fig_timeline.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6e9ef'),
            height=400,
            xaxis=dict(
                gridcolor='rgba(42, 46, 57, 0.5)',
                showgrid=True
            ),
            yaxis=dict(
                gridcolor='rgba(42, 46, 57, 0.5)',
                showgrid=True,
                title="Número de Registros"
            ),
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Statistics summary
    st.markdown('<h3 style="color: #e6e9ef;">📊 Resumen Estadístico</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_with_isin = filtered_df['isin'].notna().sum()
        perc_isin = (total_with_isin / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.markdown(f'<div style="background: linear-gradient(135deg, #7c3aed20 0%, #06b6d420 100%); padding: 1rem; border-radius: 8px; border: 1px solid #7c3aed50;"><b>Entidades con ISIN</b><br>{total_with_isin:,} ({perc_isin:.1f}%)</div>', unsafe_allow_html=True)
    
    with col2:
        total_with_folleto = filtered_df['folleto_url'].notna().sum()
        perc_folleto = (total_with_folleto / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.markdown(f'<div style="background: linear-gradient(135deg, #06b6d420 0%, #10b98120 100%); padding: 1rem; border-radius: 8px; border: 1px solid #06b6d450;"><b>Con Folleto Disponible</b><br>{total_with_folleto:,} ({perc_folleto:.1f}%)</div>', unsafe_allow_html=True)
    
    with col3:
        total_with_gestora = filtered_df['gestora_nombre'].notna().sum()
        perc_gestora = (total_with_gestora / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.markdown(f'<div style="background: linear-gradient(135deg, #10b98120 0%, #f59e0b20 100%); padding: 1rem; border-radius: 8px; border: 1px solid #10b98150;"><b>Con Gestora Asignada</b><br>{total_with_gestora:,} ({perc_gestora:.1f}%)</div>', unsafe_allow_html=True)
    
    with col4:
        total_with_depositaria = filtered_df['depositaria_nombre'].notna().sum()
        perc_depositaria = (total_with_depositaria / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.markdown(f'<div style="background: linear-gradient(135deg, #f59e0b20 0%, #ef444420 100%); padding: 1rem; border-radius: 8px; border: 1px solid #f59e0b50;"><b>Con Depositaria</b><br>{total_with_depositaria:,} ({perc_depositaria:.1f}%)</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<h3 style="color: #e6e9ef;">Top 15 Sociedades Gestoras</h3>', unsafe_allow_html=True)
    
    # Top management companies
    top_gestoras = filtered_df['gestora_nombre'].value_counts().head(15)
    
    fig_bar = go.Figure(data=[go.Bar(
        y=top_gestoras.index,
        x=top_gestoras.values,
        orientation='h',
        marker=dict(
            color=top_gestoras.values,
            colorscale=[[0, '#7c3aed'], [0.5, '#06b6d4'], [1, '#10b981']],
            showscale=True,
            colorbar=dict(
                title=dict(
                    text="Entidades",
                    font=dict(color='#e6e9ef')
                ),
                tickfont=dict(color='#e6e9ef'),
                bgcolor='rgba(30, 33, 40, 0.8)',
                bordercolor='#2a2e39',
                borderwidth=1
            )
        ),
        text=top_gestoras.values,
        textposition='outside',
        textfont=dict(color='#e6e9ef', size=11),
        hovertemplate='<b>%{y}</b><br>Entidades: %{x}<extra></extra>'
    )])
    
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e6e9ef'),
        height=600,
        xaxis=dict(
            gridcolor='rgba(42, 46, 57, 0.5)',
            showgrid=True,
            title="Número de Entidades"
        ),
        yaxis=dict(
            gridcolor='rgba(42, 46, 57, 0.5)',
            showgrid=False
        ),
        margin=dict(l=200, r=50, t=20, b=50)
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Heatmap of entity types by year
    if not timeline_df.empty:
        st.markdown('<h3 style="color: #e6e9ef;">Mapa de Calor: Registros por Tipo y Año</h3>', unsafe_allow_html=True)
        
        timeline_df['year'] = timeline_df['fecha_registro'].dt.year
        heatmap_data = timeline_df.groupby(['year', 'entity_type']).size().reset_index(name='count')
        heatmap_pivot = heatmap_data.pivot(index='entity_type', columns='year', values='count').fillna(0)
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale=[[0, '#1e2128'], [0.2, '#7c3aed'], [0.5, '#06b6d4'], [0.8, '#10b981'], [1, '#f59e0b']],
            text=heatmap_pivot.values,
            texttemplate='%{text:.0f}',
            textfont={"size": 10, "color": "white"},
            hovertemplate='<b>%{y}</b><br>Año: %{x}<br>Cantidad: %{z}<extra></extra>',
            colorbar=dict(
                tickfont=dict(color='#e6e9ef'),
                bgcolor='rgba(30, 33, 40, 0.8)',
                bordercolor='#2a2e39',
                borderwidth=1
            )
        ))
        
        fig_heatmap.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6e9ef'),
            height=500,
            xaxis=dict(title="Año", side="bottom"),
            yaxis=dict(title="Tipo de Entidad"),
            margin=dict(l=200, r=20, t=20, b=50)
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

with tab3:
    st.markdown('<h3 style="color: #e6e9ef;">Buscar y Filtrar Datos</h3>', unsafe_allow_html=True)
    
    # Search functionality
    search_term = st.text_input(
        "🔍 Buscar entidades por nombre",
        placeholder="Escriba para buscar...",
        help="Busque entidades específicas por nombre"
    )
    
    if search_term:
        search_df = filtered_df[
            filtered_df['entity_name'].str.contains(search_term, case=False, na=False)
        ]
    else:
        search_df = filtered_df
    
    # Display settings
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Default columns without 'denominacion' to avoid duplicates
        default_cols = ['entity_name', 'entity_type', 'gestora_nombre', 'fecha_registro', 'isin']
        show_cols = st.multiselect(
            "Seleccionar columnas a mostrar",
            df.columns.tolist(),
            default=default_cols
        )
    with col2:
        sort_by = st.selectbox(
            "Ordenar por",
            show_cols if show_cols else ['entity_name'],
            index=0
        )
    with col3:
        sort_order = st.radio(
            "Orden",
            ['Ascendente', 'Descendente'],
            horizontal=True
        )
    with col4:
        # Add grouping option
        group_by_entity = st.checkbox(
            "Agrupar por entidad",
            value=('denominacion' not in show_cols and 'numero' not in show_cols),
            help="Agrupa los registros por entidad cuando no se muestran las clases"
        )
    
    # Apply sorting
    ascending = sort_order == 'Ascendente'
    search_df = search_df.sort_values(sort_by, ascending=ascending)
    
    # Handle grouping to avoid duplicates
    if group_by_entity and len(show_cols) > 0:
        # Identify columns to group by (exclude class-specific columns)
        class_specific_cols = ['denominacion', 'numero', 'isin', 'fecha_alta', 'dfi']
        groupby_cols = [col for col in show_cols if col not in class_specific_cols]
        
        if groupby_cols:
            # Create aggregation dict only for non-groupby columns
            agg_cols = [col for col in show_cols if col not in groupby_cols]
            agg_dict = {}
            
            for col in agg_cols:
                if col in ['denominacion', 'numero']:
                    agg_dict[col] = lambda x: f"{len(x)} clases"
                elif col == 'isin':
                    agg_dict[col] = lambda x: ', '.join([str(i) for i in x.dropna().unique()[:3]]) + ('...' if len(x.dropna().unique()) > 3 else '')
                else:
                    agg_dict[col] = 'first'
            
            # Only aggregate if there are columns to aggregate
            if agg_dict:
                display_df = search_df[show_cols].groupby(groupby_cols, dropna=False, as_index=False).agg(agg_dict)
            else:
                # If no columns to aggregate, just drop duplicates
                display_df = search_df[show_cols].drop_duplicates()
            
            # Rename class columns if they exist
            rename_dict = {}
            if 'denominacion' in display_df.columns:
                rename_dict['denominacion'] = 'clases'
            if 'numero' in display_df.columns:
                rename_dict['numero'] = 'clases'
            
            if rename_dict:
                display_df = display_df.rename(columns=rename_dict)
        else:
            display_df = search_df[show_cols].copy()
    else:
        display_df = search_df[show_cols].copy()
    
    # Display record count
    if group_by_entity and ('denominacion' not in show_cols and 'numero' not in show_cols):
        unique_entities = search_df['entity_name'].nunique()
        st.markdown(f'<p style="color: #8b92a8;">Mostrando {len(display_df):,} entidades únicas ({len(search_df):,} registros totales)</p>', 
                   unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="color: #8b92a8;">Mostrando {len(display_df):,} registros</p>', unsafe_allow_html=True)
    
    # Format datetime columns for display
    for col in display_df.select_dtypes(include=['datetime64']).columns:
        display_df[col] = display_df[col].dt.strftime('%d/%m/%Y')
    
    # Display the dataframe
    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
        hide_index=True
    )
    
    # Download button - use original search_df for download
    csv = search_df[show_cols].to_csv(index=False)
    st.download_button(
        label="⬇️ Descargar datos filtrados como CSV",
        data=csv,
        file_name=f"entidades_filtradas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with tab4:
    st.markdown('<h3 style="color: #e6e9ef;">Análisis de Empresas</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h4 style="color: #06b6d4;">Resumen de Sociedades Gestoras</h4>', unsafe_allow_html=True)
        gestora_stats = filtered_df.groupby('gestora_nombre').agg({
            'entity_name': 'nunique',
            'entity_type': lambda x: x.value_counts().index[0] if len(x) > 0 else 'N/A'
        }).reset_index()
        gestora_stats.columns = ['Sociedad Gestora', 'Entidades Gestionadas', 'Tipo Principal']
        gestora_stats = gestora_stats.sort_values('Entidades Gestionadas', ascending=False).head(10)
        
        st.dataframe(
            gestora_stats,
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown('<h4 style="color: #10b981;">Resumen de Entidades Depositarias</h4>', unsafe_allow_html=True)
        dep_stats = filtered_df.groupby('depositaria_nombre').agg({
            'entity_name': 'nunique',
            'entity_type': lambda x: x.value_counts().index[0] if len(x) > 0 else 'N/A'
        }).reset_index()
        dep_stats.columns = ['Entidad Depositaria', 'Entidades Custodiadas', 'Tipo Principal']
        dep_stats = dep_stats.sort_values('Entidades Custodiadas', ascending=False)
        
        st.dataframe(
            dep_stats,
            use_container_width=True,
            hide_index=True
        )
    
    # Network visualization placeholder
    st.markdown('<h4 style="color: #f59e0b;">Relaciones entre Entidades</h4>', unsafe_allow_html=True)
    
    # Create a simple relationship analysis
    relationships = filtered_df[['entity_name', 'gestora_nombre', 'depositaria_nombre']].dropna()
    
    if not relationships.empty:
        # Count unique combinations
        unique_managers = relationships['gestora_nombre'].nunique()
        unique_depositaries = relationships['depositaria_nombre'].nunique()
        total_connections = len(relationships)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div style="background: linear-gradient(135deg, #7c3aed20 0%, #06b6d420 100%); padding: 1rem; border-radius: 8px; border: 1px solid #7c3aed50; text-align: center;">🔗 <b>{total_connections:,}</b><br>conexiones totales</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div style="background: linear-gradient(135deg, #06b6d420 0%, #10b98120 100%); padding: 1rem; border-radius: 8px; border: 1px solid #06b6d450; text-align: center;">🏢 <b>{unique_managers}</b><br>sociedades gestoras</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div style="background: linear-gradient(135deg, #10b98120 0%, #f59e0b20 100%); padding: 1rem; border-radius: 8px; border: 1px solid #10b98150; text-align: center;">🏦 <b>{unique_depositaries}</b><br>depositarias</div>', unsafe_allow_html=True)
        
        # Most connected entities
        st.markdown('<h5 style="color: #e6e9ef;">Gestoras Más Conectadas</h5>', unsafe_allow_html=True)
        connected = filtered_df.groupby('gestora_nombre')['depositaria_nombre'].nunique().sort_values(ascending=False).head(5)
        
        fig_connected = go.Figure(data=[go.Bar(
            x=connected.index,
            y=connected.values,
            marker=dict(
                color=connected.values,
                colorscale=[[0, '#7c3aed'], [1, '#06b6d4']],
                showscale=False
            ),
            text=connected.values,
            textposition='outside',
            textfont=dict(color='#e6e9ef', size=12),
            hovertemplate='<b>%{x}</b><br>Depositarias Conectadas: %{y}<extra></extra>'
        )])
        
        fig_connected.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6e9ef'),
            height=300,
            xaxis=dict(
                tickangle=-45,
                showgrid=False
            ),
            yaxis=dict(
                title="Número de Depositarias Conectadas",
                gridcolor='rgba(42, 46, 57, 0.5)',
                showgrid=True
            ),
            margin=dict(b=100)
        )
        st.plotly_chart(fig_connected, use_container_width=True)
    
    # Market concentration analysis
    st.markdown('<h4 style="color: #ef4444;">Concentración del Mercado</h4>', unsafe_allow_html=True)
    
    top_10_gestoras = filtered_df['gestora_nombre'].value_counts().head(10)
    market_share = (top_10_gestoras.sum() / filtered_df['gestora_nombre'].notna().sum() * 100)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Cuota de Mercado Top 10",
            value=f"{market_share:.1f}%",
            delta="de todas las entidades gestionadas"
        )
    with col2:
        herfindahl_index = ((filtered_df['gestora_nombre'].value_counts() / filtered_df['gestora_nombre'].notna().sum()) ** 2).sum()
        st.metric(
            label="Índice Herfindahl",
            value=f"{herfindahl_index:.4f}",
            delta="concentración del mercado"
        )

# Footer
st.markdown("---")
st.markdown(
    '<div style="background: linear-gradient(135deg, #7c3aed15 0%, #06b6d415 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid #7c3aed30; margin-top: 2rem;">'
    '<p style="text-align: center; color: #e6e9ef; font-size: 0.9rem; margin: 0;">'
    '📊 <b>Dashboard de Capital Riesgo Español</b><br>'
    '<span style="color: #8b92a8;">Última Actualización de Datos: ' + 
    df['fecha_registro'].max().strftime('%B %Y') + '</span></p>'
    '<p style="text-align: center; margin: 1rem 0 0 0;">'
    '<a href="https://twitter.com/Gsnchez" target="_blank" style="color: #06b6d4; text-decoration: none; font-weight: 600; margin-right: 2rem;">🐦 @Gsnchez</a>'
    '<a href="https://bquantfinance.com" target="_blank" style="color: #10b981; text-decoration: none; font-weight: 600;">🌐 bquantfinance.com</a>'
    '</p></div>',
    unsafe_allow_html=True
)
