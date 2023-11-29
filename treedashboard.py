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


# Set a specific Seaborn color palette
sns.set_palette('crest')  # You can change 'husl' to other available palettes
#sns.color_palette("cubehelix", as_cmap=True)
#sns.cubehelix_palette(start=.5, rot=-.75, as_cmap=True)

st.title('Trees in Hamburg')
st.text('Data source: Freie und Hansestadt Hamburg, Behörde für Umwelt, Klima, Energie und Agrarwirtschaft')

st.text("")
st.header('Which tree species are planted along public roads in Hamburg?')
colA1, colA2 = st.columns(2)

with colA1:
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

with colA2:
    # ### Histogram: age Distribution
    fig_age = plt.figure()
    sns.distplot(2023 - df.query('pflanzjahr>1000').query('pflanzjahr<=2023')['pflanzjahr'], kde=None)
    plt.title(f'Age of street trees in Hamburg')
    plt.ylabel('Number of trees')
    plt.xlabel('Age of the trees')
    #plt.yscale('log')
    st.pyplot(fig_age)


st.divider()    
st.text("")
st.header('Pick a tree species you want to learn more about:')

# User selects a tree species using a selectbox
default_value = 'Linde'  # Set your default value here
default_gattung_index = df['gattung_deutsch'].unique().tolist().index(default_value)
selected_gattung = st.selectbox('Select a tree species:', df['gattung_deutsch'].unique(), index=default_gattung_index)

# Filter the DataFrame based on user selection
filtered_df = df[df['gattung_deutsch'] == selected_gattung]

    
colB1, colB2 = st.columns(2)

with colB1:
   
    # Plotting with Seaborn boxplot
    fig_oak = plt.figure() #figsize=(12, 7) 
    sns.boxplot(x=filtered_df["pflanzjahr"].round(-1), y=filtered_df["stammumfang_cm"])
    plt.title(f'{selected_gattung} trees in Hamburg')
    plt.ylabel('Trunk diameter in cm')
    plt.xlabel('Year of planting')
    plt.xticks(rotation=45)  # Adjust the rotation angle as needed
    st.pyplot(fig_oak)

  
# There seem to be some outliers - identify them and clean them
# ....


with colB2:
    # ### Histogram: Treetop diameter Distribution
    # Plot a histogram of the treetop diameter
    fig_treetop = plt.figure()
    sns.distplot(filtered_df.query('kronendurchmesser_m>0')['kronendurchmesser_m'], bins=20, kde=None)
    plt.title(f'{selected_gattung} trees in Hamburg')
    plt.ylabel('Number of trees')
    plt.xlabel('Treetop diameter (m)')
    #plt.yscale('log')
    st.pyplot(fig_treetop)


st.divider()    
st.text("")
st.header('How large are the street trees in Hamburg?')
    

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
plt.xlabel('Trunk circumference in cm')
plt.ylabel('Treetop diameter in m')
plt.title('Trunk circumference in cm vs. Treetop diameter in m')

# Create a legend with unique entries
legend_entries = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=label)
                  for label, color in color_dict.items()]

plt.legend(handles=legend_entries, title='Tree species', loc='center left', bbox_to_anchor=(1, 0.5), ncol=3)

st.pyplot(fig_color)


st.divider()    
st.text("")
st.header('A closer look at the big trees')

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
plt.xlabel('Trunk circumference in cm')
plt.ylabel('Treetop diameter in m')
plt.title('Trunk circumference in cm vs. Treetop diameter in m (Filtered)')

# Create a legend with unique entries and move it outside the figure
legend_entries = [plt.Line2D([0], [0], marker=marker, color='w', markerfacecolor=color, markersize=10, label=label)
                  for label, (color, marker) in zip(color_dict.keys(), zip(colors, markers))]

plt.legend(handles=legend_entries, title='Tree species', loc='center left', bbox_to_anchor=(1, 0.5))
st.pyplot(fig_color2)



# ### Bar Plot: Trunk Circumference for Species category
# Plot, with the standard deviation as error bars
fig_trunk = plt.figure(figsize=(12, 8))
sns.barplot(x='gattung_deutsch', y='stammumfang_cm', data=df.query('stammumfang_cm>0'), ci='sd')
plt.xticks(rotation=90)
plt.title('Trunk circumference for different species')
plt.ylabel('Trunk circumference in cm')
plt.xlabel('Tree species') 
st.pyplot(fig_trunk)
    
    
