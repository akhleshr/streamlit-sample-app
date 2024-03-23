
#######################
# Importar librerias
#######################

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import io
import numpy as np
import json
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import plotly.io as pio
import time
import locale
from datetime import datetime, timedelta


# Set up the page configuration

st.set_page_config(
    page_title="Streaming Retail Data",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


#######################
# CSS styling
#######################
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: -10rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #A3CEEF;
    text-align: center;
    padding: 15px 0;
    box-shadow: 4px 4px 5px #888888;
    margin: 10px;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
# Data Collection
#######################
datos = pd.read_csv('data/bank.csv', encoding='Latin1') 
all_data = pd.read_csv('data/all_products.csv', encoding='Latin1')
total_data = pd.read_csv('data/total_products.csv', encoding='Latin1')
time_serie = pd.read_csv('data/us-retail-sales.csv')
 
#######################
# Simple Container
#######################
        
placeholder = st.empty()
start_time = datetime.now()

delta = timedelta(minutes=30)

for seconds in range(500):

    all_data['Sales_sqrt_new'] = all_data['Sales_sqrt'] * np.random.choice(np.arange(0.1, 1.5, 0.1))
    total_data['Sales_sqrt_new'] = total_data['Sales_sqrt'] * np.random.choice(np.arange(0.1, 2, 0.2))
    all_data['Minimal_Retail_Price_new'] = all_data['Minimal_Retail_Price'] * np.random.choice(np.arange(0.1, 2, 0.1))
    all_data['Visibility_sqrt_new'] = all_data['Visibility_sqrt'] * np.random.choice(np.arange(0., 3, 0.1))

    # Creating KPIs for retail products
    avg_sales = np.mean(all_data['Sales_sqrt_new'])
    avg_MRP = np.mean(all_data['Minimal_Retail_Price_new'])
    avg_visibility = np.mean(all_data['Visibility_sqrt_new'])
    
    with placeholder.container():

        st.markdown("### Real-Time Sales")

        tab1, tab2, tab3 = st.tabs(["All the Company", "By Store", "Data"])

        # Tab 1
        with tab1:

            fig_col1, fig_col2 = st.columns([4, 1])  

            with fig_col1:

                with st.expander('Description', expanded=False):
                    st.markdown(f'This first section of <span style="color:#C2185B">the dashboard displays real-time sales per square foot across product categories for the entire company</span>, accompanied by essential retail key performance indicators (KPIs).', unsafe_allow_html=True)
                    
                total_category_df = total_data[total_data['ID_store'] == 'Total']
                fig5 = px.bar(total_category_df, x='Type', y='Sales_sqrt_new',
                            labels={'Type': 'Product Category', 'Sales_sqrt': 'Sales'},
                            height=400, color='Type')

                fig5.update_layout(
                    margin=dict(l=0, r=0, t=0, b=0),
                    yaxis_title='Sales ($)',
                    font=dict(size=9),  
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-1.4,          
                        xanchor="right",
                        x=1              
                    )
                )
                fig5.update_yaxes(showticklabels=False)
                fig5.update_yaxes(range=[0, 100000])
                fig5.update_xaxes(title='')
                locale.setlocale(locale.LC_ALL, '')
                total_category_df['Sales_labels'] = total_category_df['Sales_sqrt_new'].apply(lambda x: f"${locale.format_string('%d', x, grouping=True)}")

                fig5.update_traces(text=total_category_df['Sales_labels'], textposition='auto')            
                st.markdown("### Streaming sales per square foot across product categories in all the company.")
                start_time = datetime.now()
                delta = timedelta(minutes=30)
                current_time = start_time + seconds * timedelta(seconds=50)
                current_time += timedelta(seconds=100)
                st.markdown(f"<div style='text-align: center;'><h2 style='font-size: 16px; font-weight: bold; background-color: #A3CEEF; padding: 10px;'>Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S') }</h2></div>", unsafe_allow_html=True)
                st.plotly_chart(fig5, use_container_width=True)

            with fig_col2: # KPIs
                st.markdown('<h5 style="text-align: center;"><br>Average Basic Retail KPIs</h5>', unsafe_allow_html=True)
                st.metric(label="Sales Ft Sqrt ＄", value=f'$ {round(avg_sales)}', delta=f"{(round(avg_sales) - round(np.mean(all_data['Sales_sqrt']))) / 100}%")
                st.metric(label="Minimal Price (MPR) ＄", value=f'$ {int(avg_MRP)}', delta=f"{round(((round(avg_MRP, 2) - round(np.mean(all_data['Minimal_Retail_Price'])) - 30)) / 100, 2)}%")
                st.metric(label="Visibility factor 👀", value=f"{round(avg_visibility, 2)}", delta=f"{round((round(avg_visibility) - round(np.mean(all_data['Visibility_sqrt']))/100), 4)}%")        


        # Tab 2
        with tab2:

            fig_col1, fig_col2 = st.columns([4, 2])  

            with fig_col1: 

                
                with st.expander('Description', expanded=False):
                    st.markdown(f'In this second section <span style="color:#C2185B">viewers can observe streaming sales per square foot across product categories for each individual store, along with the sales share attributed to each store, all updated in real time.</span>', unsafe_allow_html=True)


                total_category_df = total_data[total_data['ID_store'] == 'Total']

                avg_sales_by_store_type = all_data.groupby(['ID_store', 'Type'])['Sales_sqrt_new'].mean().reset_index()

                multipliers = {'OUT010': 1.01, 'OUT013': 1.5, 'OUT017': 1.1,
                               'OUT018': 1.018, 'OUT019': 3, 'OUT027': 1.03,
                               'OUT035': 1.9, 'OUT045': 1.4, 'OUT046': 1.2,
                               'OUT049': 1.002}  
                
                avg_sales_by_store_type['Sales_sqrt_new'] *= avg_sales_by_store_type['ID_store'].map(multipliers)

                avg_sales_by_store_type['Type'] = pd.Categorical(avg_sales_by_store_type['Type'], categories=all_data['Type'].unique(), ordered=True)

                avg_sales_by_store_type['rank'] = avg_sales_by_store_type.groupby('ID_store')['Sales_sqrt_new'].rank(ascending=True).astype(int)

                fig = px.bar(avg_sales_by_store_type, x='Type', y='Sales_sqrt_new', color='Type', facet_col='ID_store', facet_col_wrap=3,
                            category_orders={'Type': all_data['Type'].unique()}, height=800)  

                fig.update_layout(
                    margin=dict(l=0, r=0, t=15, b=0),                    
                    yaxis_title = '',
                    xaxis_title = '',
                    font=dict(size=9),  
                    legend=dict(
                        title ='Product Category',
                        orientation="h",
                        yanchor="bottom",      
                        y=-0.4,             
                        xanchor="right",
                        x=1                 
                    )
                )

                fig.update_yaxes(range=[0, 150], title='')
                fig.update_xaxes(title='')

                locale.setlocale(locale.LC_ALL, '')
                total_category_df['Sales_labels'] = total_category_df['Sales_sqrt_new'].apply(lambda x: f"${locale.format_string('%d', x, grouping=True)}")
                st.markdown("### Streaming sales per square foot across product categories for each store.")
                start_time = datetime.now()
                delta = timedelta(minutes=30)
                current_time = start_time + seconds * timedelta(seconds=50)
                current_time += timedelta(seconds=100)
                st.markdown(f"<div style='text-align: center;'><h2 style='font-size: 16px; font-weight: bold; background-color: #A3CEEF; padding: 10px;'>Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S') }</h2></div>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)

            with fig_col2: # Ranking

                total_sales = all_data['Sales_sqrt_new'].sum()

                total_sales_by_store = all_data.groupby('ID_store')['Sales_sqrt_new'].sum().reset_index()

                sales_share_noise = np.random.normal(loc=0, scale=2, size=len(total_sales_by_store))
                total_sales_by_store['sales_share_by_store'] = ((total_sales_by_store['Sales_sqrt_new'] / total_sales) * 100) + sales_share_noise

                total_sales_by_store = total_sales_by_store.sort_values(by='sales_share_by_store', ascending=True)

                fig6 = px.bar(total_sales_by_store, y='ID_store', x='sales_share_by_store',
                            labels={'x': 'Sales Share (%)', 'y': 'Store ID'},
                            color_continuous_scale='blues', orientation='h')

                fig6.update_traces(texttemplate='%{x:.2f}%', textposition='outside', textfont=dict(color='black'))
                fig6.update_layout(xaxis_title='Sales Share (%)', yaxis_title='', showlegend=False)

                fig6.update_traces(marker=dict(line=dict(width=0.5, color='lightblue')))  

                fig6.update_layout(plot_bgcolor='#A3CEEF', margin=dict(l=50, r=10, t=50, b=50))
                fig6.update_xaxes(range=[0, 35])

                st.markdown('<h5 style="text-align: center;"><br>Sales Share by Store</h5>', unsafe_allow_html=True)

                st.plotly_chart(fig6, use_container_width=True)

        with tab3: 

                with st.expander('Description', expanded=False):
                    st.markdown(f' The third section provides a detailed data view that you can download to observe the evolution over time and conduct your own analysis.', unsafe_allow_html=True)

                st.markdown("### Detailed Data View")
                start_time = datetime.now()
                delta = timedelta(minutes=30)
                current_time = start_time + seconds * timedelta(seconds=50)
                current_time += timedelta(seconds=100)
                st.markdown(f"<div style='text-align: center;'><h2 style='font-size: 16px; font-weight: bold; background-color: #A3CEEF; padding: 10px;'>Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S') }</h2></div>", unsafe_allow_html=True)
                st.dataframe(all_data[['ID_store', 'Type', 'Sales_sqrt_new', 'Minimal_Retail_Price_new', 'Visibility_sqrt_new']])
                time.sleep(2)
