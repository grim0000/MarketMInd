# Market Mind App
## Summary: It is an app which shows a screener with necessary info, sentimental analysis, etc and also provides an analysed list of signals provided in the web app chart.

+ The signals use Linear regression algorithm to generate signals, while taking the fundamental analysis into consideration
+ The  software displays the current price chart and volume graph in different time frames as prompted by the user
+ It uses yfinance library and basic AI to display diffrent analytical reports 
+ Has the ability to update the chart on a click of a button "Update chart"
+ Supports both NSE and BSE stocks present in the library
+ Has ML embedded to give a future prediction of the stock 
+ Gives sentimental analysis and keypoints regarding latest news about the stock
+ Gives buy sell signals on 5y timeframe 
+ Gives Fundamnetal analysis with the help of AI such as overall information and revenue about the stock


### RUNNING THE SCRIPT

+ open the folder in command line
+ pip install streamlit yfinance hashlib importlib pandas numpy scikit-learn 

### RUN THE APP
+ streamlit run app.py
+ runs on a free available local port 


