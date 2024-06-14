import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file):
    df = pd.read_excel(file, sheet_name='Keywords für kartons-zuschnitte')
    df['CPC'] = pd.to_numeric(df['CPC'], errors='coerce')
    df['CPC'] = df['CPC'].fillna(0.0)  # Setze CPC auf 0.0, wenn es None oder leer ist
    return df

def filter_data(df, volume, kd, cpc, position_range):
    filtered_df = df[
        (df['Volume'] >= volume) & 
        (df['KD'] <= kd) & 
        (df['CPC'] >= cpc) &
        (df['Current position'] >= position_range[0]) &
        (df['Current position'] <= position_range[1])
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

def plot_boxplot(df, column, title):
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=df[column], color='skyblue')
    plt.title(title)
    plt.xlabel(column)
    st.pyplot(plt)

def plot_kde(df, column, title):
    plt.figure(figsize=(10, 6))
    sns.kdeplot(df[column], color='skyblue', shade=True)
    plt.title(title)
    plt.xlabel(column)
    plt.ylabel('Density')
    st.pyplot(plt)

def display_statistics(df):
    st.write("Summary Statistics:")
    summary_stats = df.describe()
    st.dataframe(summary_stats)
    st.write("Standard Deviation:")
    st.write(df.std())
    st.write("Percentiles:")
    st.write(df.quantile([0.25, 0.5, 0.75]))

st.title('Keyword Cluster Analyzer')

uploaded_file = st.file_uploader("Upload XLS file", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("Data Loaded:")
    st.dataframe(df.head())
    st.write(f"Original DataFrame Shape: {df.shape}")

    # Removing unnecessary columns for this analysis
    df_keywords_cleaned = df.drop(columns=['Current URL', 'Updated'])

    # Display statistics
    display_statistics(df_keywords_cleaned)

    # Visualizing distributions of key metrics
    st.write("Distribution of Volume:")
    plot_boxplot(df_keywords_cleaned, 'Volume', 'Boxplot of Volume')
    plot_kde(df_keywords_cleaned, 'Volume', 'KDE of Volume')

    st.write("Distribution of KD:")
    plot_boxplot(df_keywords_cleaned, 'KD', 'Boxplot of KD')
    plot_kde(df_keywords_cleaned, 'KD', 'KDE of KD')

    st.write("Distribution of CPC:")
    plot_boxplot(df_keywords_cleaned, 'CPC', 'Boxplot of CPC')
    plot_kde(df_keywords_cleaned, 'CPC', 'KDE of CPC')

    cluster_input = st.text_area("Enter Keyword Cluster (comma-separated)")
    if cluster_input:
        # Bereinigen und Duplikate entfernen
        keywords_versanddienstleister_kartons = list(set([kw.strip() for kw in cluster_input.split(',')]))
        
        # Debug: Zeige die Länge der bereinigten Liste an
        st.write("Cleaned Cluster Length:", len(keywords_versanddienstleister_kartons))
        
        # Filtere den DataFrame basierend auf den bereinigten Keywords
        cluster_df = df[df['Keyword'].isin(keywords_versanddienstleister_kartons)]
        
        with st.expander("Filtered DataFrame"):
            st.dataframe(cluster_df)
            st.write(f"Cluster DataFrame Shape: {cluster_df.shape}")
        
        # Filteroptionen
        volume = st.slider("Minimum Volume", 0, int(df['Volume'].max()), 1000)
        kd = st.slider("Maximum KD", 0, 100, 20)
        cpc = st.slider("Minimum CPC", 0.0, float(df['CPC'].max()), 0.5)
        position_range = st.slider("Current Position Range", 0, int(df['Current position'].max()), (0, 100))

        # Anwenden der Filter
        filtered_df = filter_data(cluster_df, volume, kd, cpc, position_range)
        
        with st.expander("Filtered Cluster DataFrame"):
            st.dataframe(filtered_df)
            st.write(f"Filtered DataFrame Shape: {filtered_df.shape}")

        # Visualisierung
        st.write("Visualization:")
        plot_top_keywords(filtered_df)
