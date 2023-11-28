import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np

# Suppress FutureWarning messages
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Import data from csv file
# from the Hamburg geodata transparenz portal
# df = pd.read_csv('strassenbaumkataster_csv/strassenbaumkataster_EPSG:4326.csv')
# Load your data - read_csv should also take a zip file
df = pd.read_csv('strassenbaumkataster_csv/strassenbaumkataster_EPSG_4326.zip')

# ## Clean and Prepare Data

# ### Clean Column Names
df.columns = df.columns.str.replace('{https://registry.gdi-de.org/id/de.hh.up}', '')

# get a list of colum names
print(list(df))
# Do I need want/to clean up the tree species?

# Let's look which ones appear very few times and think about classifying them somewhere else
speciescount=df.gattung_deutsch.value_counts()
print(speciescount[speciescount < 10])

## for now I just call the ones with less than 7 "other"
#to_rename = speciescount[speciescount <= 6].index
#vother = 'Other'
#dictrename = {k:vother for k in to_rename}
#print(dictrename)
#for key in dictrename.keys():
#    df.loc[df['gattung_deutsch'].str.contains(key, flags=re.IGNORECASE), 'gattung_deutsch'] = dictrename[key]
#
## Let's look at the distribution of species now
#df.gattung_deutsch.value_counts()


# #### Adjust Data Types
# What are the data types?
df.info() # alternative: df.dtypes

# no need to convert Data Types, but let's rename cols to be more obvious
# kronenumfang is in m and stammdurchmesser is in cm
df.rename(columns={'kronendurchmesser': 'kronendurchmesser_m', 'stammumfang': 'stammumfang_cm'}, inplace=True)
# drop the ones that are just duplicates now
df.drop(columns=['kronendurchmesser_z', 'stammumfang_z'])


# ## Visualization
## Visualizations with SeaBorn

# ### Pie Chart: Species Category Distribution
# A pie chart of the tree categories
fig_pie = plt.figure(figsize=(12, 8))
tresh = len(df)/100
acount = df['gattung_deutsch'].value_counts()
bf = acount[acount > tresh]
bf['Less-than-1-percent'] = acount[acount <= tresh].sum()
bf.plot.pie()
plt.title('Hamburg Tree Species Distribution')
plt.ylabel('')
# Display the plot in Streamlit
st.pyplot(fig_pie)


fig_chestnut = plt.figure(figsize=(12,4)) 
sns.boxplot( x=df[(df["pflanzjahr"]> 1800) & (df["pflanzjahr"]< 2030) & (df["gattung_deutsch"] == "Kastanie")]["pflanzjahr"].round(-1), y=df["stammumfang_cm"] )
plt.title('Chestnut trees in Hamburg')
plt.ylabel('Trunk diameter in cm')
plt.xlabel('Year of planting')
st.pyplot(fig_chestnut)



fig_oak = plt.figure(figsize=(12,4)) 
sns.boxplot( x=df[(df["pflanzjahr"]> 1800) & (df["pflanzjahr"]< 2030) & (df["gattung_deutsch"] == "Eiche")]["pflanzjahr"].round(-1), y=df["stammumfang_cm"] )
plt.title('Oak trees in Hamburg')
plt.ylabel('Trunk diameter in cm')
plt.xlabel('Year of planting')
st.pyplot(fig_oak)


# There seem to be some outliers - identify them and clean them
# ....


# ### Bar Plot: Trunk Circumference for Species category
# Plot, with the standard deviation as error bars
fig_trunk = plt.figure(figsize=(12, 8))
sns.barplot(x='gattung_deutsch', y='stammumfang_cm', data=df.query('stammumfang_cm>0'), ci='sd')
plt.xticks(rotation=90)
plt.title('Trunk circumference for different species')
plt.ylabel('Trunk circumference in cm')
plt.xlabel('Tree species') 
st.pyplot(fig_trunk)



# ### Histogram: Treetop diameter Distribution
# Plot a histogram of the treetop diameter
fig_treetop = plt.figure(figsize=(12, 8))
sns.displot(df.query('kronendurchmesser_m>0')['kronendurchmesser_m'], bins=20, kde=False)
plt.title('Treetop diameter')
plt.ylabel('Number of trees')
plt.xlabel('Treetop diameter (m)')
st.pyplot(fig_treetop)


