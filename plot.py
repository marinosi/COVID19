import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from datetime import timedelta

def loadCovidData(src, columnName): 
    data = pd.read_csv(src) \
             .drop(['Lat', 'Long'], axis=1) \
             .melt(id_vars=['Province/State', 'Country/Region'], var_name='Date', value_name=columnName) \
             .astype({'Date':'datetime64[ns]', columnName:'Int64'})
    data['Province/State'].fillna(data['Country/Region'], inplace=True)
    data[columnName].fillna(0, inplace=True)
    return data

# Load COVID19 data.
baseURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
allData = loadCovidData(baseURL + "time_series_covid19_confirmed_global.csv", "CumCases") \
    .merge(loadCovidData(baseURL + "time_series_covid19_deaths_global.csv", "CumDeaths")) \

# Load population data, and adjust values to correspond to millions instead of thousands.
popData = pd.read_csv("population.csv")
popData['pop2020'] = popData['pop2020'] / 1000

countries = ['Italy', 'Spain', 'United Kingdom', 'France', 'Greece', 'US', 'Germany']
colors = ['blue',  'green', 'purple', 'orange', 'black', 'lightcoral', 'olive']

tmpData = allData[allData['Country/Region'].isin(countries)].loc[allData['Country/Region'] == allData['Province/State']]
startDate = tmpData.loc[tmpData['CumCases'] != 0].iloc[0,:]['Date'] - timedelta(days=1)
endDate = pd.to_datetime(tmpData.iloc[-1]['Date'])
print(startDate)


fig, (ax1, ax2, ax3) = plt.subplots(nrows=3,ncols=1, facecolor='lightgray', figsize=(15,20))

for country, col in zip(countries, colors):
  # Get country's population.
  population = popData.loc[popData['name'] == country,'pop2020'].to_numpy()[0] 

  c_df = allData.loc[(allData['Country/Region'] == country) &
                    (allData['Province/State'] == country) & (allData['Date'] >= startDate)].drop('Province/State', axis=1).copy()
  c_df['CasesGrowthR'] = c_df['CumCases'].pct_change(periods=1)*100
  c_df['CasesGrowthR'].fillna(0.0, inplace=True)
  c_df['CasesPerMillion'] = c_df['CumCases']/population
  c_df['DeathsPerMillion'] = c_df['CumDeaths']/population
  c_df['CasesGrowthR_SMA'] = c_df['CasesGrowthR'].rolling(window=7).mean()
  c_df['CasesGrowthR_EMA'] = c_df['CasesGrowthR'].ewm(span=7, adjust=True).mean()
  c_df.reset_index(inplace=True)

  # Plot the data.
  c_df.plot(ax=ax1, kind='line', linewidth=2, x='Date', y='CasesPerMillion', color=col, label=country + "(Cases)", logy=True, legend=True, grid=True)
  c_df.plot(ax=ax1, kind='line', linewidth=2, linestyle='dotted', x='Date', y='DeathsPerMillion', color=col, label=country + "(Deaths)", logy=True, legend=True, grid=True)
  c_df.plot(ax=ax2, kind='line', linewidth=2, x='Date', y='CasesGrowthR', yticks=range(0, 600, 20), color=col, label=country, legend=True, grid=True)
  # c_df.plot(ax=ax2, kind='line', linestyle='dotted', x='Date', y='CasesGrowthR_SMA', yticks=range(0, 600, 20), color=col, label=country, legend=True, grid=True)
  c_df.plot(ax=ax3, kind='line', linewidth=2, x='Date', y='CasesGrowthR_EMA', yticks=range(0, 200, 20), color=col, label=country, legend=True, grid=True)

xrange = pd.date_range(start=startDate, end=endDate)
tmpdf = pd.DataFrame({'x':xrange, '10%':[1.1**i for i in np.arange(len(xrange))], '20%':[1.2**i for i in np.arange(len(xrange))]})
tmpdf.plot(ax=ax1, kind='line', linestyle='dashed', x='x', y='10%', color='lightgrey', grid=True, label='')
tmpdf.plot(ax=ax1, kind='line', linestyle='dashdot', x='x', y='20%', color='lightgrey', grid=True, label='')

style = dict(size=10, color='gray')
med = xrange[int(len(xrange)/2)]
ax1.text(med, tmpdf[tmpdf['x'] == med]['10%']  , "$1.1^n$", **style)
ax1.text(med, tmpdf[tmpdf['x'] == med]['20%']  , "$1.2^n$", **style)


ax1.set_ylabel("# of Confirmed Incidents Per Million Inhabitants")
ax2.set_ylabel("Cases Growth Rate (%)")
ax3.set_ylabel("Cases Growth Rate (%) - Exponential Moving Average")

ax1.legend(frameon=False)
ax2.legend(frameon=False)
# plt.tight_layout()
plt.savefig("covid_data.pdf")
plt.show()
