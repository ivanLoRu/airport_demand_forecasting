## Airport Passenger Volume Forecasting
This model is a time series forecasting pipeline for monthly airport passenger demand. Classical SARIMA forecasting is used in conjunction with Monte Carlo simulation to quantify risk and uncertainty over future horizons. The project is designed to be a reproducible forecasting pipeline suitable for transportation planning, capacity analysis, and scenario simulation.

## Problem Statement
Passenger volumes in airports on a month-to-month basis carry some level of uncertainty. Sure, but there are still seasonal trends that can uncovered. This project aims to help simulate some of that uncertainty to work as an aid to airport operations, in specific, but also for any transportation agency. 

## Modeling Approach
The model can be split into three steps.
    1. Data Aggregation
    2. Forecast building
    3. Probabilistic forecasting

## Data Sources
All downloaded data came from the Bureau of Transportation Statistics, in specific, [Data Bank 28 Segment Data](https://www.bts.gov/browse-statistical-products-and-data/bts-publications/data-bank-28im-t-100-and-t-100f-internationa-0). Nonetheless, this data is somewhat messy and lacks headers for the columns. To best understand the data, please use this [key](https://www.bts.gov/sites/bts.dot.gov/files/docs/explore-topics-and-geography/topics/airlines-and-airports/230166/reference-file-db28-market-data-product_0.pdf).

## Running Locally
 A docker image of the project was created so that containers can be created locally. To run said image, use the following commands:



## Future Improvements
The biggest improvement comes from being able to synthesize data to "brush over" the humongous dip in passenger demand that occured due to the COVID pandemic. Having more data will always help, but for the development of the model, only data from Oct 2022 onwards was used. The pipeline is capable of accepting any date range of data and will create the proper files and plots, but I must figure out how to best synthesize the data to still have the assumption of stationarity present. 
The next big improvement is the creation of fuel demand forecasting. It is the next big step in the model and would help create a package for the modeling. Passenger demand is a big thing in organizing the amount of employees needed at an airport at a specific time, but fuel costs are something that can also be accounted for using forecasting methods.