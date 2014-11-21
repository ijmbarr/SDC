Summer Data Contest
===================

This git contains the ongoing project for our entry for the summer data science challenge. 

It is a collaborative work between Iain Barr and Kyle Major.

About
------
This git contains a project that acts as a twitter echo service. The twitter handle @londonpostcodes is set up to receive a tweet of a postcode and return the median house price in that area, along with a fact about that area. The data sources can be found in /Data/, an analysis of the data sources to break them down into tweetable facts can be found in /Analysis/BuildingFacts.ipynb and the python scripy that runs the service can be found in /Tools/replier.py

Tools Used
----------
To analyse the data and extract facts and ipython notebook was used, along with the numpy and pandas libraries. The compiled information was exported into a mysql database for use with the replier.

To run the replier python 2.7 was used.

Licences
---------
All raw data in this git has been obtained from various sources. We do not own the Data.

We have attempted to include details of where the original data was taken from, along with details of the licence under which it was released. 
