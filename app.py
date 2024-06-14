import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def load_data(file):
    df = pd.read_excel(file, sheet_name='Keywords für kartons-zuschnitte')
    df['CPC'] = pd.to_numeric(df['CPC'], errors='coerce')
    return df

def filter_data(df, volume, kd, cpc):
    filtered_df = df[
        (df['Volume'] >= volume) & 
        (df['KD'] <= kd) & 
        (df['CPC'] >= cpc)
    ]
    return filtered_df

def plot_top_keywords(df):
    top_20 = df.nlargest(20, 'Volume')
    plt.figure(figsize=(12, 8))
    plt.barh(top_20['Keyword'], top_20['Volume'], color='skyblue')
    plt.xlabel('Suchvolumen')
    plt.ylabel('Keyword')
    plt.title('Top 20 Keywords nach Suchvolumen')
    plt.gca().invert_yaxis()
    st.pyplot(plt)

st.title('Keyword Cluster Analyzer')

uploaded_file = st.file_uploader("Upload XLS file", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("Data Loaded:")
    st.dataframe(df.head())

    cluster_input = st.text_area("Enter Keyword Cluster (comma-separated)")
    if cluster_input:
        # Bereinigen und Duplikate entfernen
        keywords_versanddienstleister_kartons = list(set([kw.strip() for kw in cluster_input.split(',')]))
        
        # Filtere den DataFrame basierend auf den bereinigten Keywords
        cluster_df = df[df['Keyword'].isin(keywords_versanddienstleister_kartons)]
        st.write("Filtered DataFrame:")
        st.dataframe(cluster_df.head())

        # Filteroptionen
        volume = st.slider("Minimum Volume", 0, int(df['Volume'].max()), 1000)
        kd = st.slider("Maximum KD", 0, 100, 20)
        cpc = st.slider("Minimum CPC", 0.0, float(df['CPC'].max()), 0.5)

        # Anwenden der Filter
        filtered_df = filter_data(cluster_df, volume, kd, cpc)
        st.write("Filtered Cluster DataFrame:")
        st.dataframe(filtered_df.head())

        # Visualisierung
        st.write("Visualization:")
        plot_top_keywords(filtered_df)
