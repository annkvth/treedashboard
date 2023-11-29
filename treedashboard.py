import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np
from adjustText import adjust_text  # Import the adjust_text function

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


# ## Setup streamlit
# use wide mode
st.set_page_config(layout="wide")
 
st.title('Trees in Hamburg')
st.text('Data source: Freie und Hansestadt Hamburg, Behörde für Umwelt, Klima, Energie und Agrarwirtschaft')


col1, col2, col3 = st.columns(3)

with col1:
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


with col2:
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


with col3:
    # ### Bar Plot: Trunk Circumference for Species category
    # Plot, with the standard deviation as error bars
    fig_trunk = plt.figure(figsize=(12, 8))
    sns.barplot(x='gattung_deutsch', y='stammumfang_cm', data=df.query('stammumfang_cm>0'), ci='sd')
    plt.xticks(rotation=90)
    plt.title('Trunk circumference for different species')
    plt.ylabel('Trunk circumference in cm')
    plt.xlabel('Tree species') 
    st.pyplot(fig_trunk)
    
    
    

fig_color = plt.figure(figsize=(12, 8))
unique_values = df['gattung_deutsch'].unique()
colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_values)))

# Create a color dictionary
color_dict = dict(zip(unique_values, colors))

# Create a scatter plot with separate legend entries
for gattung, color in color_dict.items():
    subset_df = df[df['gattung_deutsch'] == gattung]
    plt.scatter(subset_df['stammumfang_cm'], subset_df['kronendurchmesser_m'], c=color, label=gattung)

# Add labels and a legend
plt.xlabel('Stammumfang')
plt.ylabel('Kronendurchmesser')
plt.title('Stammumfang vs. Kronendurchmesser')

# Create a legend with unique entries
legend_entries = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=label)
                  for label, color in color_dict.items()]

plt.legend(handles=legend_entries, title='Gattung Deutsch', loc='center left', bbox_to_anchor=(1, 0.5), ncol=3)

st.pyplot(fig_color)



st.text('A closer look at the big trees')

fig_color2 = plt.figure(figsize=(12, 8))
## filtering condition to include species with stammumfang larger than 500 or kronendurchmesser larger than 35
filtered_df = df[(df.groupby('gattung_deutsch')['stammumfang_cm'].transform('max') > 500) | (df['kronendurchmesser_m'] > 35)]

# Get unique values and their corresponding colors
unique_values = filtered_df['gattung_deutsch'].unique()
colors = plt.cm.viridis(np.linspace(0, 1, len(unique_values)))
markers = ['o', 's', '^', 'D', 'v', 'p', '*']  # Define different markers for each category

#  Ensure markers array is as long as the color list
markers *= (len(unique_values) // len(markers)) + 1
markers = markers[:len(unique_values)]


# Create a color dictionary
color_dict = dict(zip(unique_values, colors))
marker_dict = dict(zip(unique_values, markers))


# Create a scatter plot with separate legend entries
for gattung, color in color_dict.items():
    subset_df = filtered_df[filtered_df['gattung_deutsch'] == gattung]
    marker = marker_dict.get(gattung, 'o')  # Use 'o' as the default marker if gattung is not in the dictionary
    plt.scatter(subset_df['stammumfang_cm'], subset_df['kronendurchmesser_m'], c=color, label=gattung, marker=marker)

# Identify and annotate points that stand out (far to the right or high up)
threshold_stammumfang = 600
threshold_kronendurchmesser = 32
highlighted_points = filtered_df[(filtered_df['stammumfang_cm'] > threshold_stammumfang) | (filtered_df['kronendurchmesser_m'] > threshold_kronendurchmesser)]


texts = []
for i, row in highlighted_points.iterrows():
    text_color = color_dict.get(row['gattung_deutsch'], 'black')  # Default to black if color is not found
    texts.append(plt.text(row['stammumfang_cm'], row['kronendurchmesser_m'], str(row['pflanzjahr']), fontsize=8, color=text_color))

# Use the adjust_text function to automatically adjust the positions of the annotations to avoid overlap
adjust_text(texts)

# Add labels and a legend
plt.xlabel('Stammumfang')
plt.ylabel('Kronendurchmesser')
plt.title('Stammumfang vs. Kronendurchmesser (Filtered)')

# Create a legend with unique entries and move it outside the figure
legend_entries = [plt.Line2D([0], [0], marker=marker, color='w', markerfacecolor=color, markersize=10, label=label)
                  for label, (color, marker) in zip(color_dict.keys(), zip(colors, markers))]

plt.legend(handles=legend_entries, title='Gattung Deutsch', loc='center left', bbox_to_anchor=(1, 0.5))
st.pyplot(fig_color2)



# ### Histogram: Treetop diameter Distribution
# Plot a histogram of the treetop diameter
fig_treetop = plt.figure(figsize=(12, 8))
sns.distplot(df.query('kronendurchmesser_m>0')['kronendurchmesser_m'], bins=20, kde=None)
plt.title('Treetop diameter')
plt.ylabel('Number of trees')
plt.xlabel('Treetop diameter (m)')
st.pyplot(fig_treetop)
