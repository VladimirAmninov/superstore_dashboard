import pandas as pd
import streamlit as st
import numpy as np
import datetime as dt
import plotly.express as px

# ---- SETTING PAGE CONFIG ----
st.set_page_config(page_title="Sales dashboard",
                   page_icon=":bar_chart:",
                   layout="wide"
)

# ---- MAKING DATAFRAME ----
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel('https://github.com/VladimirAmninov/datalearn/blob/main/de101/module01/Sample%20-%20Superstore.xls?raw=true', 
                    sheet_name='Orders'
    )
    
    states = pd.read_csv('https://raw.githubusercontent.com/jasonong/List-of-US-States/master/states.csv')
    
    # Add columns to dataframe
    df['order_month_year'] = pd.to_datetime(df['Order Date']).dt.to_period('M')
    df['Date'] = pd.to_datetime(df['Order Date'].dt.strftime('%Y-%m-01'))
    df['person'] = df['Region'].replace(['West', 'East', 'Central', 'South'],['Anna Andreadi', 'Chuck Magee', 'Kelly Williams', 'Cassandra Brandow'])
    df = df.merge(states, how='left', on='State')
    return df

df=get_data_from_excel()

# ---- MAINPAGE---- 
st.title("Superstore Sales Dashboard")
st.markdown("##")

# ---- MAKING SLIDER ----
st.sidebar.header("Settings")
options = list(np.sort(df['order_month_year'].unique()))
slider_range = st.sidebar.select_slider(
    "Choose time range",
    options=options,
    value=(options[0], options[47])
)

st.sidebar.write('Time range:', slider_range[0], '-', slider_range[1])

# ----MAKING DATAFRAME SLICE
df_selection = df.query(
    "order_month_year >= @slider_range[0] & order_month_year <= @slider_range[1]"
)

# ---- KPI's ----
total_sales = int(round(df_selection["Sales"].sum(), 0))
total_profit = int(round(df_selection["Profit"].sum(), 0))
profit_ratio = int(round(100 * total_profit / total_sales, 0))

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales:")
    st.subheader(f"US $ {total_sales:,}")
with middle_column:
    st.subheader("Total Profit:")
    st.subheader(f"US $ {total_profit:,}")
with right_column:
    st.subheader("Profit Ratio:")
    st.subheader(f"{profit_ratio:,}%")

st.write('----')

# ---- SALES & PROFIT PLOTS ----
# sales and profits by time
sales_profit_main = (df_selection.groupby(['Date'])[['Sales', 'Profit']]
                                 .sum()
                                 .sort_values(by='Date'))

sales_profit_main_plot = px.line(
    sales_profit_main,
    x=sales_profit_main.index,
    y=['Profit', 'Sales'],
    title='Sales and Profit',
)

# sales and profits by regional manager
sales_profit_manager = (df_selection.groupby(['person'])[['Sales', 'Profit']]
                        .sum()
                        .sort_values(by='Sales'))

sales_profit_manager_plot = px.bar(
    sales_profit_manager,
    x=['Profit', 'Sales'],
    y=sales_profit_manager.index,
    barmode='group',
    text_auto='.2s',
    title='Sales and Profit by Regional Manager',
)

left_column, right_column = st.columns([2, 1])
left_column.plotly_chart(sales_profit_main_plot, use_container_width=True)
right_column.plotly_chart(sales_profit_manager_plot, use_container_width=True)

st.write('----')

# sales and profits by Segment, Category, Region
sales_profit_segment = (df_selection.groupby(['Segment'])[['Sales', 'Profit']]
                        .sum()
                        .sort_values(by='Sales'))

sales_profit_segment_plot = px.bar(
    sales_profit_segment,
    x=sales_profit_segment.index,
    y=['Profit', 'Sales'],
    barmode='group',
    text_auto='.2s',
    title='Sales and Profit by Segment',
)

sales_profit_category = (df_selection.groupby(['Category'])[['Sales', 'Profit']]
                        .sum()
                        .sort_values(by='Sales'))

sales_profit_category_plot = px.bar(
    sales_profit_category,
    x=['Profit', 'Sales'],
    y=sales_profit_category.index,
    text_auto='.2s',
    title='Sales and Profit by Category',
)

sales_profit_region = df_selection.groupby(['Region'])['Sales'].sum()

sales_profit_region_plot = px.pie(
    sales_profit_region,
    values='Sales',
    names=sales_profit_region.index,
    hole=.5,
    title='Sales and Profit by Region',
)

sales_profit_region_plot.update_traces(textposition='inside', textinfo='percent+label')

left_column, middle_column, right_column = st.columns(3)
left_column.plotly_chart(sales_profit_segment_plot, use_container_width=True)
middle_column.plotly_chart(sales_profit_category_plot, use_container_width=True)
right_column.plotly_chart(sales_profit_region_plot, use_container_width=True)

st.write('----')

# sales and profits by State (map)
sales_profit_state = df_selection.groupby(['Abbreviation'])['Sales'].sum()

sales_profit_state_plot = px.choropleth(sales_profit_state,
                    locations=sales_profit_state.index, 
                    locationmode="USA-states", 
                    scope="usa",
                    color='Sales',
                    color_continuous_scale="blues", 
                    
                    )

sales_profit_state_plot.update_layout(
      title_text = 'Sales by State',
      title_font_family="Sans Serif",
      title_font_size = 15,
      title_font_color="white", 
      title_x=0.45, 
         )

left_column, right_column = st.columns([10, 1])
left_column.plotly_chart(sales_profit_state_plot, use_container_width=True)

# ---- HIDE STREAMLIT STYLE ----
hide_streamlit_style = '''
                        <style>
                        #MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}
                        header {visibility: hidden;}
                        </style>
                        '''
st.markdown(hide_streamlit_style, unsafe_allow_html=True)




