# By David Maimoun
# deployed the 13.03.23
import streamlit as st
import pandas as pd
import requests             
import json 
import datetime as dt           

pd.options.mode.chained_assignment = None  # default='warn'

st.write("""
<style>
    html, body, [class*="css"]  {
    }
    h1 {
        color: #ff9f00;
    }
    h4 {
        color: gray;
        font-style: italic;
    }
    h5 {
        color: #ff9f00;;
        margin-bottom: 12px;
    }
   
   
</style>
""", unsafe_allow_html=True)

def get_chart(symbol, interval, startTime, endTime):
 
    url = URL_KLINES
    startTime = str(int(startTime.timestamp() * 1000))
    endTime = str(int(endTime.timestamp() * 1000))
    limit = '1000'
    req_params = {"symbol" : symbol, 'interval' : interval, 'startTime' : startTime, 'endTime' : endTime, 'limit' : limit}
    df = pd.DataFrame()

    try:
        df = pd.DataFrame(json.loads(requests.get(url, params = req_params).text))
        
        if (len(df.index) == 0):
            return None
     
        df = df.iloc[:, 0:6]
        df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        df.open      = df.open.astype("float")
        df.high      = df.high.astype("float")
        df.low       = df.low.astype("float")
        df.close     = df.close.astype("float")
        df.volume    = df.volume.astype("float")
        df['adj_close'] = df['close']
        df.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in df.datetime]
 
    except:
        st.warning("An error occured when fetching the data, sorry")

    
    return df

def round_value(input_value):
    if input_value.values > 1:
        a = float(round(input_value, 2))
    else:
        a = float(round(input_value, 8))
    return a

URL_KLINES = "https://api.binance.com/api/v3/klines"
URL_TICKER = "https://api.binance.com/api/v3/ticker/24hr"

df = pd.DataFrame()
try:
    df = pd.read_json(URL_TICKER)
except Exception as e: 
    st.warning("An error occured when fetching the data, sorry", e)

# SIDEBAR ###############################
st.sidebar.markdown('''
    <h1>BCP App</h1>
''',unsafe_allow_html=True)


# METRICS #############################
st.markdown('''
    <h1>Binance Crypto Price</h1>
    <h4>Get cryptocurrency price in Real Time !</h4>
    <hr style="height:1px;border:none;background-color:lightgrey;" />
    <h5>Dashboard 📈</h5>

''',unsafe_allow_html=True)
if not df.empty:
    currencies = st.sidebar.multiselect(
        f"Currencies ({len(df)})",
        df.symbol, 
        ['BTCUSDT', 'ETHBTC', 'SHIBBUSD', 'DOGEBUSD', 'BNBBTC']
    )

    col1, col2, col3 = st.columns(3)
    id = 1
    for currency in currencies:
        data = df[df.symbol == currency]
        price = round_value(data.weightedAvgPrice)
        percent = f'{float(data.priceChangePercent)}%'
        if id == 1:
            col1.metric(currency, price, percent)
        if id == 2:
            col2.metric(currency, price, percent)
        if id == 3:
            col3.metric(currency, price, percent)
            id = 0
        id += 1


    # CHART ########################################################
    st.markdown('''
        <hr style="height:1px;border:none;background-color:lightgrey;" />
        <h5>Chart 💹</h5>
    ''',unsafe_allow_html=True)
    year = dt.datetime.now().year
    current_month = dt.datetime.now().month
    current_day = dt.datetime.now().day

    col4, col5 = st.columns([1,4])
    with col4:
        currency = st.selectbox('Currency', df['symbol'])
        date_selected = st.slider(
            'Months',
            min_value= 1,
            max_value= 12,
            value=(12))
    if st.button('Get Chart!'):
        with col5:
            with st.spinner(f'Fetching the data for {currency}...'):
                # Create a list of first day of every month in 2020
                months = [dt.datetime(year-1, i, 1) for i in range(1, date_selected+1)]
                months.append(dt.datetime.now())
                # Call the function for every date range
                df_list = [get_chart('ETHUSDT', '1h', months[i], months[i+1] - dt.timedelta(0, 1)) for i in range(0, len(months) - 1)]
                # Concatenate list of dfs in 1 df
                df_chart = pd.concat(df_list)
                st.line_chart(df_chart ['close'].astype('float'))


    # DATA TABLE ###########################################
    st.markdown('''
        <hr style="height:1px;border:none;background-color:lightgrey;" />
        <h5>All Prices 💲</h5>
    ''',unsafe_allow_html=True)

    st.dataframe(df)

    st.markdown('<br><br><p><i>By David Maimoun</p></i>',unsafe_allow_html=True)  
    
