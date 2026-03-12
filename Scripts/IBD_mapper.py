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

    if IBDtsv:              # if the file exists read its content into a pandas df
        IBDdf = pd.read_csv(IBDtsv, sep="\t")

    # then the excel file containing the location and population information
    LocationXlxs = st.file_uploader("Choose your Excel file with location/population information:",
                                    type=["xlsx"])

    if LocationXlxs:    # if the file exists load it into a pandas df
        Locationdf = pd.read_excel(LocationXlxs, header = 0)
        Locationdf = Locationdf[~Locationdf["Lat."].isin(['..'])]           # delete all rows where latitude = '..'
        Locationdf = Locationdf[~Locationdf["Long."].isin(['..'])]          # delete all rows where longiture = '..'
        Locationdf["Lat."] = pd.to_numeric(Locationdf["Lat."], errors="coerce")         # make sure the whole lat column is numeric
        Locationdf["Long."] = pd.to_numeric(Locationdf["Long."], errors="coerce")       # make sure the whole long column is numeric
        Locationdf = Locationdf.dropna(subset=["Lat.", "Long."])            # delete all na that might have been created in the previous step
        Locationdf = Locationdf.rename(columns={                            # for simplicity rename the columns
        "Lat.": "lat",
        "Long.": "lon"})

    return IBDdf, Locationdf                                                # return the df IBDdf and Locationdf


## Before displaying the map we ask the User to select populations/individuals ##

def SelectandFilter(Locationdf):
    popList = st.multiselect(                                   # ask the user to select populations from all populations in the file
        "First, select populations you want to display:",
        options=Locationdf["Locality"].unique(),
        default=None
    )
    Locationdf_filtered = Locationdf[Locationdf["Locality"].isin(popList)]      # filter the Locationdf to only contain selected populations
    
    if popList is not None:                                     # ask the user to specify which individuals to compare from the above selected populations
        indivList = st.multiselect(
            "Now selecet specific individuals to display (or all):",
            options=Locationdf_filtered["Master ID"].unique(),
            default=None
        )
        Locationdf_filtered = Locationdf_filtered[Locationdf_filtered["Master ID"].isin(indivList)]     # filter the dataset further to only contain the individuals
    return Locationdf_filtered


## render a map with all datapoints ##
def MapCreator(IBDdf, Locationdf_filtered):

    SubsetLocationdf = Locationdf_filtered[["lat", "lon"]]          # first create a subset of the Locationdf to only contain latitude and longitude
    st.write(SubsetLocationdf)
    # Generate the map point layer
    if SubsetLocationdf is not None:                                # if the Subsetlocationdf is not None
        pointLayer = pdk.Layer(                                     # create the point layer of the PyDeck
            "ScatterplotLayer", 
            data=SubsetLocationdf,                                  # using Subsetlocationdf as data
            get_position = '[lon, lat]',                            # the lon and lat columns as data points
            get_radius = 10000,                                     # get a point radius of 10000
            get_fill_color = [0, 255, 0],                           # make them green
        )

        view_state = pdk.ViewState(                                 # specify the initial viewstate
            latitude=float(SubsetLocationdf["lat"].mean()),         # as the mean of the lat and long coordinates of the plotted points
            longitude=float(SubsetLocationdf["lon"].mean()),
            zoom=5)

        st.pydeck_chart(                                            # finally create the map using the above specified layers
            pdk.Deck(
                layers=[pointLayer], 
                initial_view_state=view_state))
        

## Finally run all pre defined functions step by step

IBDdf, Locationdf = Fileupload()

if IBDdf is not None and Locationdf is not None:
    Locationdf_filtered = SelectandFilter(Locationdf)
    st.write(Locationdf_filtered)
    st.write(IBDdf)
    if Locationdf_filtered is not None:   
        MapCreator(IBDdf, Locationdf_filtered)