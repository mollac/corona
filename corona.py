# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

DATE_TIME = "date/time"
DATA_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
FILE_C = "time_series_19-covid-Confirmed.csv"
FILE_D = "time_series_19-covid-Deaths.csv"
FILE_R = "time_series_19-covid-Recovered.csv"

st.title("Corona virus")
st.markdown('The source data can be found [here](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series)!')

def load_data(the_file):
    data = pd.read_csv(the_file)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data.rename(columns={'long': 'lon', 'country/region':'country', 'province/state':'state'}, inplace=True)
    data['country'] = data['country'].str.replace('Mainland China', 'China')
    data['state'] = data['state'].str.replace('Diamond Princess cruise ship', 'DP ship')
    data['confirmed'] = data.iloc[:,-1:]
    data['state'].fillna(' ', inplace=True)
    data.fillna(0, inplace=True)
    return data

def create_layer(data_frame, elev_scale, radius, colors):
    return pdk.Layer(
        'HexagonLayer',
        data = data_frame,
        get_position = ['lon', 'lat'],
        auto_highlight = True,
        elevation_scale = elev_scale,
        radius = radius,
        elevation_range = [0, 1000],
        pickable = False,
        extruded = True,
        color_range = [colors for x in range(6)],
        coverage = 1)

df_d = load_data(DATA_URL + FILE_D)
df_r = load_data(DATA_URL + FILE_R)
df = load_data(DATA_URL + FILE_C)

df['deads'] = df_d['confirmed']
df['recovered'] = df_r['confirmed']

df = df[['country', 'state', 'lat', 'lon', 'confirmed', 'deads', 'recovered']]
st.subheader('The generated dateset.')
st.dataframe(df)

all_cases = int(df.confirmed.sum())
all_deads = int(df.deads.sum())
all_recovered = int(df.recovered.sum())

st.subheader('Statistic by countries')
gr_country = df[['country', 'confirmed', 'deads', 'recovered']].groupby(['country']).sum()
st.write(gr_country)

st.subheader('Statistic by countries/states')
gr_country_state = df[['country','state','confirmed', 'deads', 'recovered']].groupby(['country', 'state']).sum()
st.write(gr_country_state)

st.markdown(f'Confirmed cases: **{all_cases}**, deads: **{all_deads}** \
    ({round(all_deads/all_cases * 100,2)}%), recovered: **{all_recovered}** \
    ({round(all_recovered/all_cases * 100,2)}%)')


df_confirmed = []
df_deads = []
df_recovered = []

lat = list(df.lat)
lon = list(df.lon)
country = list(df.country)
confirmed = list(df.confirmed)
deads = list(df.deads)
recovered = list(df.recovered)

for d in range(1,df.shape[0]):
    for x in range(confirmed[d]):
        df_confirmed.append([country[d], lon[d], lat[d], confirmed[d]])
    for x in range(deads[d]):
        df_deads.append([country[d], lon[d], lat[d], deads[d]])
    for x in range(recovered[d]):
        df_recovered.append([country[d], lon[d], lat[d], recovered[d]])

d_c = pd.DataFrame(data=df_confirmed, columns=['country', 'lon', 'lat','confirmed'])
d_d = pd.DataFrame(data=df_deads, columns=['country', 'lon', 'lat','deads'])
d_r = pd.DataFrame(data=df_recovered, columns=['country', 'lon', 'lat','recovered'])

if st.checkbox('Show world map'):
    midpoint = (np.average(d_c["lon"]), np.average(d_c["lat"]))
    view_state = pdk.ViewState(
        longitude = midpoint[0],
        latitude  = midpoint[1],
        zoom = 3,
        min_zoom = 1,
        max_zoom = 15,
        pitch = 40.5)

    layer_c = create_layer(d_c, all_cases//100, 20000, (50, 200, 50))
    layer_d = create_layer(d_r, all_recovered//100, 24000, (50, 50, 200))
    layer_r = create_layer(d_d, all_deads//100, 28000, (200, 50, 50))
    r = pdk.Deck(layers = [layer_c, layer_r, layer_d], initial_view_state = view_state)
    st.markdown('Green: **CONFIRMED** Blue: **RECOVERED** Red: **DIED**')
    st.write(r)
    
