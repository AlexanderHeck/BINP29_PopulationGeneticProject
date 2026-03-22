#!/usr/bin/python

'''
IBD_mapper.py

Description: This is the script for a streamlit based web application. Two input files (one file with IBD connections and one file with coordinate and time data) are processed with multiple
             user inputs to create a graphical map showing the spatial positions of the datapoints and their IBD connections.

User-defined functions:
        Fileupload(): handling the file upload into the streamlit interface
        SelectandFilter(Locationdf): handling the user directed filtering of the input data
        IBD_selector(Locationdf_filtered, IBDdf): merging the filtered location data with the IBD length fragments, returning a combined dataframe
        IBD_cutoffFilter(IBD_coordsdf): letting the user further filter the combined dataframe based on IBD length thresholds
        IBD_normalizer(IBD_coordsdf): creating a new column in the combined dataset with normalized IBD length data
        IBD_colorizer(IBD_norm): creating a new column in the combined dataset with rgb values according to the normalized data
        MapCreator(IBD_coordsdf, Locationdf_filtered): using both the filtered location and the combined dataframes to create a map of the positions of samples and their IBD connections


        
Non-standard modules: 
    streamlit: used to run the interactive interface
    pandas: used to read in and handle dataframes
    pydeck: used to create the map
    matplotlib.pyplot: used to create a histogram to let the user view the distribution of IBD segment lengths
    matplotlib.cm: used to assign color values to the normalised IBD lengths

Procedure:
    1. Have the user upload their files
    2. Prompt the user to select which timeframe, countries and indiviuals to display and filter the data accordingly
    3. Use the filtered location data and the full IBD data to create a merged dataset with all shared IBD lengths for all individuals accross chromosomes
    4. Plot a histogram of the distribution of all IBD lengths and let the user define cutoff thresholds for IBD length shared between individuals
    5. Filter the merged/combined dataset according to the user defined IBD thresholds
    6. Normalize the IBD lengths and use the normalized values to assign colors to each IBD length
    7. Plot the map by first creating a point layer with all selected data and then a line layer connecting indivuals color coded by the length of their shared IBDs

Input: location_time.xlsx IBD_connections.tsv
Output: graphical output of the map
    
Usage:
streamlit run IBD_mapper.py

Version: 1.00
Date: 2026-03-22
Name: Alexander Heck

'''

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import matplotlib.cm as cm

## Let the User upload their files ##

def Fileupload():
    
    IBDdf = None            # initialise empty variables
    Locationdf = None
    
    # first the tsv file containing the IBD segments
    IBDtsv = st.file_uploader("Choose your IBD file in tsv format:", type=["tsv"])

    if IBDtsv is None:              # if the file does not exist, issue a warning
        st.warning("Please upload a IBD file.")
        st.stop()
    else:                           # else load it into a pandas df
        IBDdf = pd.read_csv(IBDtsv, sep="\t")

    # then the excel file containing the location and population information
    LocationXlxs = st.file_uploader("Choose your Excel file with location/population information:",
                                    type=["xlsx"])
    if LocationXlxs is None:        # if the file does not exist, issue a warning and halt the code
        st.warning("Please upload a location file.")
        st.stop()
    else:                           # if the file exists load it into a pandas df
        Locationdf = pd.read_excel(LocationXlxs, header = 0)
        Locationdf = Locationdf.replace("..", pd.NA)                        # replace '..' with NA
        Locationdf["Lat."] = pd.to_numeric(Locationdf["Lat."], errors="coerce")         # make sure the whole lat column is numeric
        Locationdf["Long."] = pd.to_numeric(Locationdf["Long."], errors="coerce")       # make sure the whole long column is numeric
        Locationdf = Locationdf.dropna(subset=["Lat.", "Long."])            # delete all na that might have been created in the previous step
        Locationdf = Locationdf.rename(columns={                            # for simplicity rename the columns
        "Lat.": "lat",
        "Long.": "lon"})

    return IBDdf, Locationdf                                                # return the df IBDdf and Locationdf


## Before displaying the map we ask the User to select populations/individuals ##

def SelectandFilter(Locationdf):
    # the variable timeFrame saves the user input on which period of time they want to look at
    timeFrame = st.selectbox('Select Time Period:', ['Prehistory (before 5000 BCE)',
                                                     'Stone Age (5000 - 3000 BCE)',
                                                     'Bronze Age (3000 - 1000 BCE)',
                                                     'Iron Age (1000 - 550 BCE)',
                                                     'Antiquity (550 BCE - 500 CE)',
                                                     'Middle Ages (500 - 1500 CE)',
                                                     'Modern Period (1500 to now)'], index=None)

    if timeFrame is not None:                       # if the user has selected a time frame, the following statements filter the Locationdf by date of the individual and put out a filtered dataframe
        if timeFrame == 'Prehistory (before 5000 BCE)':
            Locationdf_filtered=Locationdf[Locationdf["Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]"]>=7000]
        elif timeFrame == 'Stone Age (5000 - 3000 BCE)':
            Locationdf_filtered = Locationdf[Locationdf["Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]"]<=7000]
            Locationdf_filtered = Locationdf_filtered[Locationdf_filtered["Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]"]>=5000]
        elif timeFrame == 'Bronze Age (3000 - 1000 BCE)':
            Locationdf_filtered = Locationdf[Locationdf["Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]"]<=5000]
            Locationdf_filtered = Locationdf_filtered[Locationdf_filtered["Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]"]>=3000]
        elif timeFrame == 'Iron Age (1000 - 550 BCE)':
            Locationdf_filtered = Locationdf[Locationdf["Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]"]<=3000]
            Locationdf_filtered = Locationdf_filtered[Locationdf_filtered["Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]"]>=2550]
        elif timeFrame == 'Antiquity (550 BCE - 500 CE)':
            Locationdf_filtered = Locationdf[Locationdf["Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]"]<=2550]
            Locationdf_filtered = Locationdf_filtered[Locationdf_filtered["Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]"]>=1500]
        elif timeFrame == 'Middle Ages (500 - 1500 CE)':
            Locationdf_filtered = Locationdf[Locationdf["Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]"]<=1500]
            Locationdf_filtered = Locationdf_filtered[Locationdf_filtered["Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]"]>=500]
        elif timeFrame == 'Modern Period (1500 to now)':
            Locationdf_filtered = Locationdf[Locationdf["Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]"]<=500]
    else:
        st.warning("Please select a time period.")
        st.stop()    
    
    
    popList = st.multiselect(                                   # ask the user to select populations from all populations in the file
        "Select populations you want to display:",
        options=Locationdf_filtered["Political Entity"].unique(),
        default=None)
    Locationdf_filtered = Locationdf_filtered[Locationdf_filtered["Political Entity"].isin(popList)]      # filter the Locationdf to only contain selected populations
    
    if popList is not None:                                     # ask the user to specify which individuals to compare from the above selected populations
        indivList = st.multiselect(
            "Now selecet specific individuals to display (or all):",
            options=Locationdf_filtered["Master ID"].unique(),
            default=None)
        Locationdf_filtered = Locationdf_filtered[Locationdf_filtered["Master ID"].isin(indivList)]     # filter the dataset further to only contain the individuals
    return Locationdf_filtered


## The following code extracts coordinates and matches them with IBD values if they have any

@st.cache_data(ttl=3600)
def IBD_selector(Locationdf_filtered, IBDdf):
    idList = Locationdf_filtered["Genetic ID"]                                              # create a list with only the ids of interest
    IBDdf_filtered = IBDdf[IBDdf['iid1'].isin(idList) & IBDdf['iid2'].isin(idList)]         # create a new list containing only iid1 and iid2 that are in the id List
    IBDperPair = IBDdf_filtered.groupby(["iid1", "iid2"])["lengthM"].sum()                  # sum up the lengthM per id pair accross chromosomes
    IBDperPair = IBDperPair.reset_index()                                                   # reset the dataframe index
    coordsdf = Locationdf_filtered[['Genetic ID', 'lon', 'lat']]                            # save a new dataframe only containing the genetic id, longitude and latitude
    IBD_coordsdf = IBDperPair.merge(coordsdf, left_on='iid1', right_on='Genetic ID', how='left').drop(columns = 'Genetic ID')       # merge coordsdf and IBDperPair together by adding the coords of iid1
    IBD_coordsdf = IBD_coordsdf.merge(coordsdf, left_on='iid2', right_on='Genetic ID', how='left', suffixes = ('1', '2')).drop(columns = 'Genetic ID') # merge a second time adding coords of iid2
    return IBD_coordsdf


## The following function allows for further filtering of the IBD and coordinates dataframe

def IBD_cutoffFilter(IBD_coordsdf):
    # the first step is to give the user an overview over the data by creating a histogram
    fig, ax = plt.subplots()        # create empty subplots
    ax.hist(IBD_coordsdf['lengthM'], bins = 100)         # select the column and number of bins
    ax.set_ylabel("Frequency")                          # set the y-label
    ax.set_xlabel("IBD length [cM]")                    # set the x-label
    ax.set_title("Histogram of IBD lengths")            # set the title
    ax.set_yscale("log")                                # set the 
    st.pyplot(fig)                                      # have streamlit output the plot
    st.write("Please select IBD connection thresholds you would like to apply:")
    ibdMin = st.number_input("Minimum IBD length [cM]:")    # select a minimum ibd length
    ibdMax = st.number_input("Maximum IBD length [cM]:")    # select a maximum ibd length
    if ibdMax is not None and ibdMin is not None:           # filter the dataframe if thresholds were selected
        IBD_coordsdf = IBD_coordsdf[IBD_coordsdf["lengthM"]>=ibdMin]
        IBD_coordsdf = IBD_coordsdf[IBD_coordsdf["lengthM"]<=ibdMax]    
    return IBD_coordsdf

## The following function adds a color column to the IBD_coordsdf dataframe ##

@st.cache_data(ttl=3600)
def IBD_normalizer(IBD_coordsdf):
    # First normalise IBD values to scale from 0 to 1 according to the formula xnorm = (x - xmin)/(xmax-xmin)
    minIBD = IBD_coordsdf['lengthM'].min()
    maxIBD = IBD_coordsdf['lengthM'].max()
    IBD_coordsdf['lengthM_norm'] = (IBD_coordsdf['lengthM']-minIBD)/(maxIBD-minIBD)
    return IBD_coordsdf

@st.cache_data(ttl=3600)
def IBD_colorizer(IBD_norm):
    cmap = cm.get_cmap("plasma")    # save the colornap plasma as cmap
    r,g,b,_ = cmap(IBD_norm)        # apply the colormap to the current value, saving the output separately as r, g, and b components
    return [int(r*255), int(g*255), int(b*255)] # return a list with the rgb values times 255

## render a map with all datapoints ##

def MapCreator(IBD_coordsdf, Locationdf_filtered):
    SubsetLocationdf = Locationdf_filtered[["lat", "lon"]]          # first create a subset of the Locationdf to only contain latitude and longitude
    st.write("Map creation started")
    SubsetLocationdf = SubsetLocationdf[SubsetLocationdf["lat"].notna()]
    SubsetLocationdf = SubsetLocationdf[SubsetLocationdf["lon"].notna()]
    if SubsetLocationdf.empty:
        st.warning("No individuals selected to display on the map.")
        return
    # Generate the map point layer
    if SubsetLocationdf is not None:                                # if the Subsetlocationdf is not None
        
        pointLayer = pdk.Layer(                                     # create the point layer of the PyDeck
            "ScatterplotLayer", 
            data=SubsetLocationdf,                                  # using Subsetlocationdf as data
            get_position = '[lon, lat]',                            # the lon and lat columns as data points
            get_radius = 10000,                                     # get a point radius of 10000
            get_fill_color = [0, 255, 0],                           # make them green
            pickable=True)                                          # make them pickable
        
        view_state = pdk.ViewState(                                 # specify the initial viewstate
            latitude=float(SubsetLocationdf["lat"].mean()),         # as the mean of the lat and long coordinates of the plotted points
            longitude=float(SubsetLocationdf["lon"].mean()),
            zoom=5)
        
        plot_ibd = st.checkbox(label="Plot IBD connections?", value = True)

        if plot_ibd:                                                # if the user wants to print the IBD values
            lineLayer = pdk.Layer(                                  
                "LineLayer",                                        # create the line layer
                data=IBD_coordsdf,                                  # using IBD_coordsdf as data
                get_source_position='[lon1, lat1]',                 # define the source point
                get_target_position='[lon2, lat2]',                 # define the target point
                get_color='color',                                  # color according to the column "color"
                get_width=1,                                        # set width to 1
                pickable=True)                                      # make them pickable
            st.pydeck_chart(                                            # finally create the map using the above specified layers
                pdk.Deck(
                    layers=[pointLayer, lineLayer], 
                    initial_view_state=view_state))
        else:
            st.pydeck_chart(                                            # finally create the map using the above specified layers
                pdk.Deck(
                    layers=[pointLayer], 
                    initial_view_state=view_state))
        

## Finally run all pre defined functions step by step

IBDdf, Locationdf = Fileupload()                                    # uploading all files

Locationdf_filtered = SelectandFilter(Locationdf)                   # filter dataset

if Locationdf_filtered is not None:
    IBD_coordsdf = IBD_selector(Locationdf_filtered, IBDdf)         # calculate IBD segments and add everything to one dataframe
    IBD_coordsdf = IBD_cutoffFilter(IBD_coordsdf)                   # cutoff and filter the merged dataset
    IBD_coordsdf = IBD_normalizer(IBD_coordsdf)                     # add a column with normalized IBD lengths
    IBD_coordsdf['color'] = IBD_coordsdf['lengthM_norm'].apply(IBD_colorizer)   # apply the colorize function to every item in the normalized IBD length column

if IBD_coordsdf is not None and Locationdf_filtered is not None:
    MapCreator(IBD_coordsdf, Locationdf_filtered)                   # create the map output

