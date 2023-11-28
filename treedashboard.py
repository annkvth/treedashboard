import streamlit as st
import seaborn as sns
import pandas as pd
 
# Load your data
df = pd.read_csv('tree.csv')
 
# Create a Seaborn correlation plot
plot = sns.heatmap(df.corr(), annot=True)
 
# Display the plot in Streamlit
st.pyplot(plot.get_figure())

