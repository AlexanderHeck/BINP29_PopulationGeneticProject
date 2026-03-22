# IBD mapper tool #
### Population Genetics Project BINP29 ###
### Author: Alexander Heck ###

A simple interactive web interface to create a graphical map output showing the coordinates of ancient individuals and their IBD connections.

## Setting up a virtual environment ##
Using conda, I set up a virtual environment using python version 3.14.3.
```bash
conda create -n "PopGenProject" python=3.14.3
conda activate "PopGenProject"
```
Additional python modules needed are:
 - pandas (2.3.3)
 - pydeck (0.9.1)
 - matplotlib (10.8.8)

## Running the app ##
The app is run using streamlit. To make the app work, we need to install streamlit in the current environment using conda.
```bash
conda install streamlit
streamlit --version  # Streamlit, version 1.55.0
```

To run the web app type:
```bash
streamlit run IBD_mapper.py
```
And open the link to a local host created by streamlit. In the app, you can select your input files, timeframe, populations, individuals, and IBD connection cutoffs.
For the script to work you need certain named columns in your input files:

For the IBD dataset:
 - lengthM: containing the length of the IBD segment in centimorgan
 - iid1 and iid2: genetic ids of compared individuals

In the AADR annotation dataset:
 - Genetic ID: the genetic id of the individuals, same as in iid1 and iid2
 - Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]: containing how many years before 1950 the individual lived
 - Political Entity: in what state the sample was found
 - Lat. and Long.: the coordinates of the sample