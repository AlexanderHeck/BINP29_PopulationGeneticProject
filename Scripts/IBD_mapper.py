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
    
    IBDdf = None
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

    return IBDdf, Locationdf

IBDdf, Locationdf = Fileupload()
IBDdf
Locationdf
## render a map with all datapoints ##
Locationdf["Lat."] = pd.to_numeric(Locationdf["Lat."], errors="coerce")
Locationdf["Long."] = pd.to_numeric(Locationdf["Long."], errors="coerce")
Locationdf = Locationdf.dropna(subset=["Lat.", "Long."])
Locationdf = Locationdf.rename(columns={
    "Lat.": "lat",
    "Long.": "lon"})

SubsetLocationdf = Locationdf[["lat", "lon"]]

st.write(type(Locationdf))
st.write(Locationdf.head())
st.write(Locationdf.dtypes)

# Generate the map point layer
if SubsetLocationdf is not None:
    pointLayer = pdk.Layer(
        "ScatterplotLayer", 
        data=SubsetLocationdf,
        get_position = '[lon, lat]',
        get_radius = 10000,
        get_fill_color = [255, 0, 0],
    )

    view_state = pdk.ViewState(
        latitude=float(SubsetLocationdf["lat"].mean()),
        longitude=float(SubsetLocationdf["lon"].mean()),
        zoom=5)

    st.pydeck_chart(
        pdk.Deck(
            layers=[pointLayer], 
            initial_view_state=view_state))