import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Path to the logo
logo_path = 'HTML-CSS/buscom_logo.jpeg'

# Streamlit layout with logo and title
col1, col2 = st.columns([1, 6])

with col1:
    st.image(logo_path, width=100)

with col2:
    st.title('RFP Summary')
    st.subheader('ChatGPT Extractions Simulations Analysis')

# File uploader in Streamlit
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Ensure the DataFrame contains the required columns
    if 'field' in df.columns and 'chatgpt_value' in df.columns and 'config' in df.columns:
        fields = st.multiselect('Select fields to plot', df['field'].unique())
        
        for field in fields:
            # Filter DataFrame based on the selected field
            df_filtered = df[df['field'] == field]
            # Group data by chatgpt_value and config, and count occurrences
            df_grouped = df_filtered.groupby(['chatgpt_value', 'config']).size().reset_index(name='counts')
            
            # Create a bar plot using seaborn with a bright color palette
            plt.figure(figsize=(14, 8))
            bar_plot = sns.barplot(data=df_grouped, x='chatgpt_value', y='counts', hue='config', ci=None, palette='bright')
            
            # Enhance labels and ticks for visibility
            plt.title(f'Counts of ChatGPT Values by Config for {field}', fontsize=20)
            plt.xlabel('ChatGPT Value', fontsize=18)
            plt.ylabel('Counts', fontsize=18)
            plt.xticks(rotation=45, ha='right', fontsize=16)
            plt.yticks(fontsize=16)
            plt.legend(title='Config', fontsize=14, title_fontsize='16')
            plt.tight_layout()
            st.pyplot(plt)
    else:
        st.error("The uploaded CSV does not have the required 'field', 'chatgpt_value', and 'config' columns.")
