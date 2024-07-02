# Option Long Call/Put Prediction Model
## Defined Objects
### Parameters Dictionary
- defined values for all parameters included in the functions for the batch call
- can be scaled up; more functions can be added
### Export CSV Function
- creates a "data" folder in the CWD if none exists
- exports a DataFrame as a specifically named CSV file or utilizes the name of the DataFrame being passed into the function
- exported CSV name will always be prefixed with YYYY-MM-DD
- all CSV files are exported to the "data" folder
### Generate Features Function
- generates features for the DataFrames extracted from the batch call
### Prep Data Function
- preps the DataFrames for model training purposes
### Extract Sentiment Function
- filters through the returned JSON object from AlphaVantage's sentiment function for the sentiment of the specified stock symbol
- wraps it up in a DataFrame
### Set Time Index Function
- sets a time index for all returned DataFrames
### Alpha Supercall Function
- allows a user to make multiple calls to AlphaVantage's API
- all API calls being made would need to have their parameters presents in the "Parameters Dictionary"
- returns a DataFrame for each call type as a tuple so that all of them can be unpacked into their own DataFrame
- executes the "Extract Sentiment" function if a sentiment call is made
- indexes all returned DataFrames by their time column
