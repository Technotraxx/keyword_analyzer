import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests

def load_data(file):
    df = pd.read_excel(file, sheet_name='Keywords für kartons-zuschnitte')
    df['CPC'] = pd.to_numeric(df['CPC'], errors='coerce')
    df['CPC'] = df['CPC'].fillna(0.0)  # Setze CPC auf 0.0, wenn es None oder leer ist
    return df

def fetch_ahrefs_data(api_key, target_url):
    url = "https://api.ahrefs.com/v3/site-explorer/organic-keywords"
    params = {
        "country": "de",
        "date": "2024-06-14",
        "limit": 100,
        "mode": "prefix",
        "order_by": "sum_traffic:desc",
        "protocol": "both",
        "select": "keyword,serp_features,volume,keyword_difficulty,cpc,sum_traffic,sum_paid_traffic,best_position,best_position_url,best_position_kind,best_position_has_thumbnail,best_position_has_video,serp_target_positions_count,last_update,language",
        "target": target_url,
        "volume_mode": "monthly"
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
    return response.json()

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

def plot_histogram(df, column, title, log_scale=False):
    plt.figure(figsize=(10, 6))
    plt.hist(df[column], bins=30, color='skyblue', edgecolor='black')
    plt.title(title)
    plt.xlabel(column)
    plt.ylabel('Frequency')
    if log_scale:
        plt.yscale('log')
    st.pyplot(plt)

def plot_kde(df, column, title):
    plt.figure(figsize=(10, 6))
    sns.kdeplot(df[column], color='skyblue', shade=True)
    plt.title(title)
    plt.xlabel(column)
    plt.ylabel('Density')
    st.pyplot(plt)

def display_statistics(df):
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    st.write("Summary Statistics:")
    summary_stats = numeric_df.describe()
    st.dataframe(summary_stats)

st.title('Keyword Cluster Analyzer')

# Eingabe für den API-Schlüssel und die Ziel-URL
api_key = st.text_input("Enter your Ahrefs API Key", type="password")
target_url = st.text_input("Enter the target URL")

# Option zum Hochladen einer XLS-Datei oder Abrufen von Daten über die API
data_source = st.radio("Select data source", ("Upload XLS file", "Fetch from Ahrefs API"))

if data_source == "Upload XLS file":
    uploaded_file = st.file_uploader("Upload XLS file", type=["xlsx"])
    if uploaded_file:
        df = load_data(uploaded_file)
        st.write("Data Loaded:")
        st.dataframe(df.head())
        st.write(f"Original DataFrame Shape: {df.shape}")
elif data_source == "Fetch from Ahrefs API" and api_key and target_url:
    try:
        data = fetch_ahrefs_data(api_key, target_url)
        df = pd.json_normalize(data['organic_keywords'])
        df.columns = df.columns.str.replace('keyword_difficulty', 'KD')
        df.columns = df.columns.str.replace('volume', 'Volume')
        df.columns = df.columns.str.replace('cpc', 'CPC')
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
        df['KD'] = pd.to_numeric(df['KD'], errors='coerce')
        df['CPC'] = pd.to_numeric(df['CPC'], errors='coerce').fillna(0.0)
        st.write("Data Fetched from Ahrefs API:")
        st.dataframe(df.head())
        st.write(f"Original DataFrame Shape: {df.shape}")
    except Exception as e:
        st.error(f"Error fetching data from Ahrefs API: {e}")

if 'df' in locals():
    # Removing unnecessary columns for this analysis
    df_keywords_cleaned = df.drop(columns=['best_position_url', 'last_update'])

    # Display statistics
    display_statistics(df_keywords_cleaned)

    # Visualizing distributions of key metrics
    st.write("Distribution of Volume:")
    plot_histogram(df_keywords_cleaned, 'Volume', 'Histogram of Volume', log_scale=True)

    st.write("Distribution of KD:")
    plot_kde(df_keywords_cleaned, 'KD', 'KDE of KD')

    st.write("Distribution of CPC:")
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
        position_range = st.slider("Current Position Range", 0, int(df['best_position'].max()), (0, 100))

        # Anwenden der Filter
        filtered_df = filter_data(cluster_df, volume, kd, cpc, position_range)
        
        with st.expander("Filtered Cluster DataFrame"):
            st.dataframe(filtered_df)
            st.write(f"Filtered DataFrame Shape: {filtered_df.shape}")

        # Visualisierung
        st.write("Visualization:")
        plot_top_keywords(filtered_df)
