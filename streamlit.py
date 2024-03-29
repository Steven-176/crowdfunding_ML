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

st.write('## Analyse des projets de crowdfunding')
st.markdown("<br>", unsafe_allow_html=True)
st.write('### Problématique : "Quels sont les facteurs déterminants du succès des projets sur Kickstarter ?"')
st.markdown("<br>", unsafe_allow_html=True)
st.write('### Influence de la catégorie du projet sur son succès')
st.markdown("<br>", unsafe_allow_html=True)

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

# # ---------------------- Visualisation des projets par état pour une année spécifique ----------------------

# @st.cache_resource
# def plot_graph_by_year(selected_year):
#     data_selected_year = clean_crowdfunding_2018_filtered[(clean_crowdfunding_2018_filtered['year'] == selected_year) & 
#                                                           (clean_crowdfunding_2018_filtered['state'].isin(['successful', 'failed', 'live']))]


#     fig, ax = plt.subplots(figsize=(10, 6))
#     sns.countplot(data=data_selected_year, x='state', ax=ax)
#     plt.title(f"Nombre de projets par état pour l'année {selected_year}")
#     plt.xlabel("État du projet")
#     plt.ylabel("Nombre de projets")

#     st.pyplot(fig)

# unique_years = sorted(clean_crowdfunding_2018_filtered['year'].unique())
# unique_years = [year for year in unique_years if 2015 <= year <= 2018]

# selected_year = st.select_slider('Sélectionnez une année', options=unique_years)

# plot_graph_by_year(selected_year)

@st.cache_resource
def plot_graph_category(selected_year, state):
    # Filtrer les données pour l'année sélectionnée
    data_selected_year = clean_crowdfunding_2018_filtered[(clean_crowdfunding_2018_filtered['year'] == selected_year) & 
                                                          (clean_crowdfunding_2018_filtered['state'].isin(['successful', 'failed']))]
    
    # Calculer le nombre de projets réussis et échoués pour chaque catégorie pour l'année sélectionnée
    success_failure_by_category_year = data_selected_year.groupby(['main_category', 'state']).size().unstack()
    success_failure_by_category_year['total'] = success_failure_by_category_year['successful'].fillna(0) + success_failure_by_category_year['failed'].fillna(0)

    fig, ax = plt.subplots(figsize=(12, 8))
    if state == 'success':
        sns.barplot(data=success_failure_by_category_year, x=success_failure_by_category_year.index, y='successful', color='green', ax=ax)
        plt.title("Nombre de projets réussis par catégorie pour l'année " + str(selected_year))
    else:
        sns.barplot(data=success_failure_by_category_year, x=success_failure_by_category_year.index, y='failed', color='red', ax=ax)
        plt.title("Nombre de projets échoués par catégorie pour l'année " + str(selected_year))
    plt.xlabel("Catégorie principale du projet")
    plt.ylabel("Nombre de projets")
    plt.ylim(0, 6000)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Sélectionner les années uniques
unique_years = sorted(clean_crowdfunding_2018_filtered['year'].unique())
unique_years = [year for year in unique_years if 2015 <= year <= 2017]

# Sélectionner une année avec un slider
selected_year = st.select_slider('Sélectionnez une année', options=unique_years)

# Stocker l'état actuel et l'année sélectionnée dans la session
current_state = st.session_state.get("current_state", "success")
st.session_state["selected_year"] = selected_year

# Afficher le graphique correspondant lorsque l'utilisateur sélectionne une autre année dans le slider
if st.button("Afficher les succès / échecs"):
    if current_state == "success":
        plot_graph_category(selected_year, 'failure')
        st.session_state["current_state"] = "failure"
    else:
        plot_graph_category(selected_year, 'success')
        st.session_state["current_state"] = "success"
else:
    # Afficher automatiquement le graphique des projets réussis pour la première année dans le slider
    plot_graph_category(selected_year, current_state)
