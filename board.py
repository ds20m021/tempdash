#https://stdworkflow.com/127/error-command-errored-out-with-exit-status-1-when-install-geopandas
import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static #https://pypi.org/project/streamlit-folium/
#import geopandas as gpd
import seaborn as sns
import requests
import time
#st.set_page_config(layout="wide")

st.title('Global Temperatures')

@st.cache
def load_data():
    data = pd.read_csv('GlobalLandTemperaturesByCountry.csv', parse_dates=['dt'])
    data = data[["Country", "dt", "AverageTemperature"]]
    data['year'] = data["dt"].dt.year
    data = data.dropna(axis=0)
    data_raw=data.loc[:,:]

    data = data.groupby(['year', 'Country']).agg({'AverageTemperature': 'mean'}).reset_index()
    worldData = data.groupby(['year']).agg({'AverageTemperature': 'mean'}).reset_index()
    worldData['Country'] = "World"
    data = pd.concat([data, worldData])
    #data = data.rename(columns={'year': 'index'}).set_index('index')
    return (data,data_raw)



data_load_state = st.text('Loading data...')
data,data_raw = load_data()
data_load_state.text('')

predURL = "https://ds20m008-autopublisher-project.azurewebsites.net/"




year_to_filter = st.slider('year', min_value=1743, max_value=2013, step=1, value=1950)
selected_country = "Italy"
r = requests.get(predURL+'countries')
cs=None
if r.status_code == 200:
    cs = r.json()["countries"]
    cs.remove("World")
    selected_country = st.selectbox("Which country to compare?", cs )

pal = sns.color_palette(["#001c7f","#001c7f","#001c7f","#b1400d","#b1400d","#b1400d"])







#violine plots
data_violin=data.loc[data.Country.isin(cs),:]

#create palette
my_pal={}

for c in cs:
    if c==selected_country:
        my_pal[c]="red"
    else:
        my_pal[c]="gray"

fig = plt.figure(figsize=(10, 4))
sns.violinplot(x=data_violin["Country"], y=data_violin["AverageTemperature"],palette=my_pal)
st.pyplot(fig)



#facet plot
data_of_country=data_raw.loc[data_raw.Country==selected_country,:]
data_of_country=data_of_country.loc[(data_of_country["year"]>year_to_filter) & (data_of_country["year"]<year_to_filter+5),:]


#fig = plt.figure(figsize=(10, 4))
ridge_plot = sns.FacetGrid(data_of_country, row="year", hue="year", aspect=5, height=1.25)
ridge_plot.map(sns.kdeplot, "AverageTemperature", clip_on=False, shade=True, alpha=0.7, lw=4, bw=.2)
ridge_plot.map(plt.axhline, y=0, lw=4, clip_on=False)

st.pyplot(ridge_plot)




fig = plt.figure()

dsp = data[data["Country"] == "World"]
filtered = dsp[dsp["year"] < year_to_filter]
sns.lineplot(data=dsp, x="year", y="AverageTemperature", alpha=0.3, palette=pal)
sns.lineplot(data=filtered, x="year", y="AverageTemperature", alpha=1, palette=pal, label='World')
preddata = filtered.sort_values(by="year",ascending=False)
if preddata["year"].count() > 10:
    body = list(preddata.head(10)["AverageTemperature"])
    r = requests.post(predURL+"World", json=body)
    if r.status_code == 200:
        predresult = pd.DataFrame({"year": list(range(year_to_filter, year_to_filter+10)), "AverageTemperature": r.json()["temperatures_predicted"]})
        sns.lineplot(data=predresult, x="year", y="AverageTemperature", alpha=1, palette=pal, label= "World prediction")


dsp = data[data["Country"] == selected_country]
filtered = dsp[dsp["year"] < year_to_filter]
sns.lineplot(data=dsp, x="year", y="AverageTemperature", alpha=0.3, palette=pal)
sns.lineplot(data=filtered, x="year", y="AverageTemperature", alpha=1, palette=pal, label=selected_country)
preddata = filtered.sort_values(by="year",ascending=False)
if preddata["year"].count() > 10:
    body = list(preddata.head(10)["AverageTemperature"])
    r = requests.post(predURL+selected_country, json=body)
    if r.status_code == 200:
        predresult = pd.DataFrame({"year": list(range(year_to_filter, year_to_filter+10)), "AverageTemperature": r.json()["temperatures_predicted"]})
        sns.lineplot(data=predresult, x="year", y="AverageTemperature", alpha=1, palette=pal,
                     label=selected_country + " prediction")




st.pyplot(fig)



##animated temp plot
fig, ax = plt.subplots()

ax.set_xlabel("Year")
ax.set_ylabel("AverageTemperature")
ax.set_title("Average Temperature")


avg_temperatures=dsp.groupby(by="year").agg({'AverageTemperature': 'mean'}).reset_index()
avg_temperatures_selection=avg_temperatures.loc[(avg_temperatures.year>=year_to_filter-10) & (avg_temperatures.year<=year_to_filter+11),:]


ax.set_ylim(0, avg_temperatures_selection.AverageTemperature.max()*1.4)


animated_line_temp_plot, = ax.plot(avg_temperatures_selection.year, avg_temperatures_selection.AverageTemperature)
the_plot = st.pyplot(plt)




def animate(year_offset):
    year_to_predict=list(avg_temperatures_selection.year)[year_offset]
    print("year to predict: " + str(year_to_predict))
    #get prediction
    previous_values=avg_temperatures.loc[(avg_temperatures.year>=year_to_predict-10) & (avg_temperatures.year<year_to_predict),"AverageTemperature"]
    #print(previous_values)
    body = list(previous_values)
    r = requests.post(predURL+selected_country, json=body)
    if r.status_code == 200:
        curr_plot=ax.plot(range(year_to_predict,year_to_predict+10), r.json()["temperatures_predicted"], color='tab:orange')
        ax.axvline(list(avg_temperatures_selection.year)[year_offset],color="orange")
        #print(str(avg_temperatures.year))
        ax.set_title("Prediction at " + str(year_to_predict))
        ax.set_xlabel("Year")
        ax.set_ylabel("Temperature")
        the_plot.pyplot(plt)
        return curr_plot
    return None

def start_animation():
    for year_offset in range(0,10):
        res=animate(year_offset)
        #time.sleep(0.1)
        if(res!=None):
            ax.lines.pop(1)
            ax.lines.pop(1)

if st.button("Animate"):
    start_animation()





###geo json



geoJSON_df = gpd.read_file("countries.geo.json")
#countries = pd.read_csv("countries.geo.json")
mapdata = data[(data["year"] == year_to_filter) & (data["Country"] != "World")][["Country", "AverageTemperature"]]
mapdata = mapdata.merge(geoJSON_df, left_on='Country', right_on='admin', how='left')[["Country","AverageTemperature","geometry"]]
mapdata = mapdata.dropna(subset=["geometry"])
geo = gpd.GeoSeries(mapdata.set_index('Country')['geometry']).to_json()
#st.dataframe(data=mapdata)
#st.line_chart(dsp['AverageTemperature'])

m = folium.Map(location=[0,0],zoom_start=1)
c = folium.Choropleth(
    geo_data=geo,
    name="test",
    data=mapdata,
    columns=["Country", "AverageTemperature"],
    key_on="feature.id",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    highlight= True
)

style_function = lambda x: {'fillColor': '#ffffff',
                            'color':'#000000',
                            'fillOpacity': 0.1,
                            'weight': 0.1}

highlight_function = lambda x: {'fillColor': '#000000',
                                'color':'#000000',
                                'fillOpacity': 0.50,
                                'weight': 0.1}

#c.geojson.add_child(
#    folium.features.GeoJsonTooltip(
#        fields=["id"],
#        #aliases=['Country', "Average Temperature"],
#        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
#    )
#)
c.add_to(m)

geojson1 = folium.features.GeoJson(
    data=gpd.GeoDataFrame(mapdata),
    smooth_factor=2,
    style_function=lambda x: {'color':'black','fillColor':'transparent','weight':0.5},
    tooltip=folium.features.GeoJsonTooltip(
        fields=['Country', "AverageTemperature"],
        aliases=['Country', "Average Temperature"],
                 sticky=False,
                 labels=True,
                 style="background-color: #F0EFEF;border: 2px solid black;border-radius: 3px;box-shadow: 3px;", max_width=800),
    highlight_function=lambda x: {'weight':3,'fillColor':'grey'}
).add_to(m)

#NIL = folium.features.GeoJson(
#    #geo_data=geo,
##    data=mapdata,
##    style_function=style_function,
##    control=False,
##    highlight_function=highlight_function,
##    tooltip=folium.features.GeoJsonTooltip(
##        fields=["Country", "AverageTemperature"],
##        aliases=['Country', "Average Temperature"],
##        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
##    )
##)
#m.add_child(c)
#m.keep_in_front(NIL)





#folium.features.GeoJson()
folium_static(m)




