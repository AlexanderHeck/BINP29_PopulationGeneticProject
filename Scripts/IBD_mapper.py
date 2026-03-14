#!/usr/bin/python

'''
IBD_mapper.py

Description: This program takes 3 input files: a .faa file, the results of a blastp search of that file in .blastp format, and a uniprot database. It then identifies scaffolds in the .faa
             file that contain genes from a bird species, i.e. whos first match in the blast search was from a bird species.

User-defined functions:
        ScaffoldIdentifier(fastaName, queryID): This function takes a queryID and searches a provided fasta file for the corresponding scaffold
        BirdFinder(uniprotName, acList): This function takes a list of species accessions and searches a uniprot database and returns only bird species ids.
        AcQueryDictCreator(blastpName): This function takes in a file in blastp Format and outputs a dictionary of queryID and species accessions of their first hit in blastp.

Non-standard modules: 
    sys: here it is used to allow for command line arguments to be passed onto this script
    
Procedure:
    1. Save the command line arguments
    2. Run AcQueryDictCreator to create a Dictionary of species accessions and query ID
    3. Run BirdFinder to identify those accessions belonging to birds
    4. Run ScaffoldIdentifier to find the scaffolds to wich the queryIDs linked to bird genes are found and write them in a simple .txt file

Input: AA fasta file, blastp File, uniprot database
Output: Output txt file
    
Usage:
python3 datParserAlex.py \
FastaFile.faa \
Blastpfile.blastp \
OutputFile.txt \
uniprotDatabase.dat

Example: 
python3 datParserAlex.py \
../Output/Haemoproteus/ParsedGtf/gffParse.faa \
../Output/Haemoproteus/ParsedGtf/Haemoproteus_blast.blastp \
../Output/Haemoproteus/ParsedGtf/birdScaffolds.txt \
uniprot_sprot.dat

Version: 1.00
Date: 2022-03-02
Name: Alexander Heck

'''

import streamlit as st
import pandas as pd
import pydeck as pdk

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
        st.write(Locationdf)
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
        st.write(Locationdf_filtered)                           # write the current filtered dataframe to check    
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
'''
Okay so what this function does, it makes a list of all to plot indiv. Then it goes through every line in the IBD file and checks that both  iid1 and 2 are present in the list,
if so. If both are present it retrieves the length M, normalises it to values between 0 and 1 and adds a color, and returns the dataframe containing coordinates for each dataoint,
IBD, normalised IBD, and a color
'''

def IBD_selector(Locationdf_filtered, IBDdf):
    idList = Locationdf_filtered["Genetic ID"]
    st.write(idList)
    st.write(IBDdf)
    IBDdf_filtered = IBDdf[IBDdf['iid1'].isin(idList) & IBDdf['iid2'].isin(idList)]
    st.write('writing filtered ibdf')
    st.write(IBDdf_filtered)
    IBDperPair = IBDdf_filtered.groupby(["iid1", "iid2"])["lengthM"].sum()
    IBDperPair = IBDperPair.reset_index()
    st.write(IBDperPair)
    coordsdf = Locationdf_filtered[['Genetic ID', 'lon', 'lat']]
    st.write(coordsdf)
    IBD_coordsdf = IBDperPair.merge(coordsdf, left_on='iid1', right_on='Genetic ID', how='left').drop(columns = 'Genetic ID')
    st.write('First merge:')
    st.write(IBD_coordsdf)
    IBD_coordsdf = IBD_coordsdf.merge(coordsdf, left_on='iid2', right_on='Genetic ID', how='left', suffixes = ('1', '2')).drop(columns = 'Genetic ID')
    st.write('2nd merge:')
    st.write(IBD_coordsdf)
    return IBD_coordsdf
    

## render a map with all datapoints ##
def MapCreator(IBD_coordsdf, Locationdf_filtered):
    SubsetLocationdf = Locationdf_filtered[["lat", "lon"]]          # first create a subset of the Locationdf to only contain latitude and longitude
    st.write(SubsetLocationdf)
    st.write("Map creation started")
    SubsetLocationdf = SubsetLocationdf[SubsetLocationdf["lat"].notna()]
    SubsetLocationdf = SubsetLocationdf[SubsetLocationdf["lon"].notna()]
    if SubsetLocationdf.empty:
        st.warning("No individuals selected to display on the map.")
        return
    datatype = SubsetLocationdf["lon"].dtype
    st.write("datatype investigated")
    datatype
    # Generate the map point layer
    if SubsetLocationdf is not None:                                # if the Subsetlocationdf is not None
        lineLayer = pdk.Layer(
            "LineLayer",
            data=IBD_coordsdf,
            get_source_position='[lon1, lat1]',
            get_target_position='[lon2, lat2]',
            get_color=[0, 255, 0],
            get_width=1)
        
        pointLayer = pdk.Layer(                                     # create the point layer of the PyDeck
            "ScatterplotLayer", 
            data=SubsetLocationdf,                                  # using Subsetlocationdf as data
            get_position = '[lon, lat]',                            # the lon and lat columns as data points
            get_radius = 10000,                                     # get a point radius of 10000
            get_fill_color = [0, 255, 0])                           # make them green
        
        view_state = pdk.ViewState(                                 # specify the initial viewstate
            latitude=float(SubsetLocationdf["lat"].mean()),         # as the mean of the lat and long coordinates of the plotted points
            longitude=float(SubsetLocationdf["lon"].mean()),
            zoom=5)
        
        st.pydeck_chart(                                            # finally create the map using the above specified layers
            pdk.Deck(
                layers=[pointLayer, lineLayer], 
                initial_view_state=view_state))
        

## Finally run all pre defined functions step by step

IBDdf, Locationdf = Fileupload()

Locationdf_filtered = SelectandFilter(Locationdf)

if Locationdf_filtered is not None:
    IBD_coordsdf = IBD_selector(Locationdf_filtered, IBDdf)

st.write("Going into map creation now")
if IBD_coordsdf is not None and Locationdf_filtered is not None:
    MapCreator(IBD_coordsdf, Locationdf_filtered)



'''
### Further Implemetation ###
- Caching
- Color coded IBD thickness
- Further downstream filtering of strength of IBD connection using scale
'''