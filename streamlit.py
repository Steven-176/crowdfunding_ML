import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
# import folium
# from sklearn.preprocessing import StandardScaler
# from sklearn.decomposition import PCA
# from sklearn.cluster import KMeans

crowdfunding_2018 = pd.read_csv('ks-projects-201801.csv')

# Nettoyage des données
crowdfunding_2018['state'] = crowdfunding_2018['state'].replace('undefined', pd.NA)
crowdfunding_2018.dropna(inplace=True)
crowdfunding_2018['launched'] = pd.to_datetime(crowdfunding_2018['launched'])
crowdfunding_2018['deadline'] = pd.to_datetime(crowdfunding_2018['deadline'])
crowdfunding_2018['usd_pledged_real'] = crowdfunding_2018['usd_pledged_real'].round(2)
crowdfunding_2018['days_to_deadline'] = (crowdfunding_2018['deadline'] - crowdfunding_2018['launched']).dt.days
crowdfunding_2018['year'] = crowdfunding_2018['launched'].dt.year
crowdfunding_2018['month'] = crowdfunding_2018['launched'].dt.strftime('%B')

crowdfunding_2018['percentage_reached'] = (crowdfunding_2018['usd_pledged_real'] / crowdfunding_2018['usd_goal_real']) * 100

clean_crowdfunding_2018 = crowdfunding_2018.drop(['launched', 'deadline', 'name', 'goal', 'pledged', 'usd pledged'], axis=1)

Q1 = clean_crowdfunding_2018['usd_pledged_real'].quantile(0.25)
Q3 = clean_crowdfunding_2018['usd_pledged_real'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

clean_crowdfunding_2018_filtered = clean_crowdfunding_2018[(clean_crowdfunding_2018['usd_pledged_real'] >= lower_bound) & (clean_crowdfunding_2018['usd_pledged_real'] <= upper_bound)]

success_by_category = clean_crowdfunding_2018_filtered.groupby(['main_category', 'state']).size().unstack()

success_by_category['total'] = success_by_category['successful'] + success_by_category['failed']

@st.cache_resource
def plot_graph_category(state):
    fig, ax = plt.subplots(figsize=(12, 8))
    if state == 'success':
        sns.barplot(data=success_by_category, x=success_by_category.index, y='successful', color='green', ax=ax)
        plt.title("Nombre de projets réussis par catégorie")
    else:
        sns.barplot(data=success_by_category, x=success_by_category.index, y='failed', color='red', ax=ax)
        plt.title("Nombre de projets échoués par catégorie")
    plt.xlabel("Catégorie principale du projet")
    plt.ylabel("Nombre de projets")
    plt.xticks(rotation=45)
    st.pyplot(fig)



if st.button("Afficher les succès / échecs"):
    current_state = st.session_state.get("current_state", "success")
    if current_state == "success":
        plot_graph_category('failure')
        st.session_state["current_state"] = "failure"
    else:
        plot_graph_category('success')
        st.session_state["current_state"] = "success"

# ---------------------- Visualisation des projets par état pour une année spécifique ----------------------

@st.cache_resource
def plot_graph_by_year(selected_year):
    data_selected_year = clean_crowdfunding_2018_filtered[(clean_crowdfunding_2018_filtered['year'] == selected_year) & 
                                                          (clean_crowdfunding_2018_filtered['state'].isin(['successful', 'failed', 'live']))]


    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(data=data_selected_year, x='state', ax=ax)
    plt.title(f"Nombre de projets par état pour l'année {selected_year}")
    plt.xlabel("État du projet")
    plt.ylabel("Nombre de projets")

    st.pyplot(fig)

unique_years = sorted(clean_crowdfunding_2018_filtered['year'].unique())
unique_years = [year for year in unique_years if 2015 <= year <= 2018]

selected_year = st.select_slider('Sélectionnez une année', options=unique_years)

plot_graph_by_year(selected_year)