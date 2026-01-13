# finstreet-round2-ml-trading
End to End ML Trading system using FYERS API for Finstreet Round 2


The proper sequence of running the code is as follows:
1. fyers_fetch_rites.py
    - this will save a file called rites_daily.csv in data/raw
2. build_features.py
    - this will save a file called rites_features.csv in data/processed
3. train.py
    - this is where the model learns.
    - we use a 80/20 split for the model to learn and test
    - the model gives each feature some weightage according to as and when that feature signal matches with the target
4. predict.py
    - this program predicts the price movements for the next 5 trading days
    - the program first predicts for jan 1 using dec 31 features
    - since the features of jan 1 are required to predict movements for jan 2 we use the real fetched features for jan 1 and use them to predict jan 2 and so on.
    - only nov-dec data is used to train the model and jan data is only used to predict
5. main.py
    - this applies the strategy and risk management rules and decides when to purchase the shares
6. orders.py
    - this implements orders through the FYERS API
