import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
#st.set_page_config(layout="wide")

st.title('Global Temperatures')

@st.cache
def load_data():
    data = pd.read_csv('GlobalLandTemperaturesByCountry.csv', parse_dates=['dt'])
    data = data[["Country", "dt", "AverageTemperature"]]
    data['year'] = data["dt"].dt.year
    data = data.dropna(axis=0)

    data = data.groupby(['year', 'Country']).agg({'AverageTemperature': 'mean'}).reset_index()
    #data = data.rename(columns={'year': 'index'}).set_index('index')
    return data



data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('')

dsp = data[(data["Country"] == "Austria") | (data["Country"] == "Norway")]
import matplotlib
import seaborn as sns
#matplotlib.rcParams['axes.grid'] = True
#matplotlib.rcParams['savefig.transparent'] = True
dsp = data[(data["Country"] == "Austria") | (data["Country"] == "Norway")]
fig = plt.figure()
sns.lineplot(data=dsp, x="year", y="AverageTemperature", hue="Country")

st.pyplot(fig)


countries = pd.read_csv('countries.txt')
mapdata = data[data["year"] == 2010][["Country", "AverageTemperature"]]
mapdata = countries.merge(mapdata, left_on='Name', right_on='Country', how='left')
#st.line_chart(dsp['AverageTemperature'])

m = folium.Map(location=[0,0],zoom_start=1)
folium.Choropleth(
    geo_data="countries.geo.json",
    name="test",
    data=mapdata,
    columns=["Country", "AverageTemperature"],
    key_on="feature.properties.name",
    fill_color="YlOrRd",
    fill_opacity=0.7
).add_to(m)
#folium.features.GeoJson()
folium_static(m)
