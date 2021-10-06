import pandas as pd
import numpy as np
#import chart_studio.plotly as py
import cufflinks as cf
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
#####
# Plotly funcionar no Jupyter Notebook
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)
cf.go_offline()
import investpy as inv
import matplotlib.pyplot as plt
import datetime as dt
###############################################################################

data_inicio = '01/01/2020'
data_fim = dt.date.today().strftime('%d/%m/%Y')


#Criando side bar
st.sidebar.header('Pairs')

#Carregando as moedas
currency_data = np.array(inv.get_currency_crosses_list())
currency_choice = st.sidebar.selectbox('Select the pair', currency_data)

#Data Inicio
start_date = st.sidebar.text_input('Data início', data_inicio)
end_date = st.sidebar.text_input('Data final', data_fim)

if start_date > end_date:
    st.write('Data de início não pode ser menor que a data final')

#Selecionando os dados
currency = inv.get_currency_cross_historical_data(currency_cross=currency_choice, from_date=start_date, 
                                                  to_date=end_date, interval = 'daily')
del currency['Currency']


#Adicionando coluna LN:
ln = []
for c in range(len(currency)):
    if c > 0:
        ln.append(((currency['Close'][c]/currency['Close'][c-1])-1)*100)
    else:
        ln.append(0)
currency['LN'] = ln

#Adicionando coluna média
currency['Media'] = currency['LN'].rolling(window=16).mean()

#Adicionando coluna desvio retornos
currency['Desvio_Retornos'] = currency['LN'].rolling(window=16).std()

#Adicionando coluna BAIXA/ALTA:
currency['ALTA/BAIXA'] = np.where((currency['Open']>currency['Close']),0,1)

#Adicionando Volatilidade Modificada
currency['Volatilidade Modificada'] = np.where((currency['ALTA/BAIXA']==1),
                                               currency['Desvio_Retornos']*1,currency['Desvio_Retornos']*-1)

#Adicionando Volatilidade Acumulada
currency['Volatilidade_Acumulada'] = currency['Volatilidade Modificada'].rolling(window=16).sum()

#Adicionando Total Pips
#currency['Total_Pips'] = (currency['Close'] - currency['Open']) * 10000

st.title('Table')
st.write(currency.tail(5))
st.title('Volatility')
st.write(currency['Volatilidade_Acumulada'].tail(2))


#Grafico
st.title('Volatility')
fig = sns.displot(currency, x='Volatilidade_Acumulada',bins=10)
st.pyplot(fig)

st.markdown('97%')
st.write(currency['Volatilidade_Acumulada'].std()*2+currency['Volatilidade_Acumulada'].mean())
st.markdown('2%')
st.write((currency['Volatilidade_Acumulada'].std()*2)*-1+currency['Volatilidade_Acumulada'].mean())
