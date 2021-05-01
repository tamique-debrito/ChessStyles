This repository is my exploration of ML for chess.
There are three main parts:

    (1) Getting and formatting data (from chess.com via web-scraping + public API)
    (2) Loading data into machine-learnable form (dependent on both the collected data format and the machine learning architecture)
    (3) Machine-learn the data
    
Currently (1) is done. (2) and (3) don't have any defined goals, so they don't necessarily have criteria for "done-ness".
However I've started exploration with a basic architecture.

The Dataset package deals with (1) and (2):

    (1) Collection, validation, and formatting of data:
        > Scrape user info from web
        > Select users and download their game info until dataset criteria are met
        > Compute additional info from downloaded files
    (2) Data loading for machine learning:
        > Load data and convert to correct format for each ML architecture defined in (3)

The Architectures package deals with (3):

    (3) Define machine learning architectures/experiments that may be interesting to explore