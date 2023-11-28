import streamlit as st
import seaborn as sns
import pandas as pd
 
# Load your data - read_csv should also take a zip file
df = pd.read_csv('strassenbaumkataster_csv/strassenbaumkataster_EPSG_4326.zip')

# insert the column rename parts here

# Create a Seaborn correlation plot
plot = sns.heatmap(df.corr(), annot=True)
 
# Display the plot in Streamlit
st.pyplot(plot.get_figure())

