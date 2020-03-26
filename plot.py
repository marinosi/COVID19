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
popData['pop2020'] = popData['pop2020'].apply(lambda x : x/1000)

countries = ['Italy', 'Spain', 'United Kingdom', 'France', 'Netherlands','Greece']
colors = ['blue',  'green', 'purple', 'orange', 'red', 'black']

tmpData = allData[allData['Country/Region'].isin(countries)].loc[allData['Country/Region'] == allData['Province/State']]
startDate = tmpData.loc[tmpData['CumCases'] != 0].iloc[0,:]['Date'] - timedelta(days=1)
print(startDate)

fig, (ax1, ax2) = plt.subplots(nrows=1,ncols=2, sharex=True)

for country, col in zip(countries, colors):
  c_df = allData.loc[(allData['Country/Region'] == country) &
                    (allData['Province/State'] == country) & (allData['Date'] >= startDate)].copy()
  c_df['CasesGrowthR'] = c_df['CumCases'].pct_change(periods=1)*100
  c_df['CasesGrowthR'].fillna(0.0, inplace=True)
  c_df.reset_index(inplace=True)

  # Plot the data.
  c_df.plot(ax=ax1, kind='line', x='Date', y='CumCases', color=col, label=country + "(Cases)", logy=True, legend=True, grid=True)
  c_df.plot(ax=ax1, kind='line', linestyle='--', x='Date', y='CumDeaths', color=col, label=country + "(Deaths)", logy=True, legend=True, grid=True)
  c_df.plot(ax=ax2, kind='line', x='Date', y='CasesGrowthR', yticks=range(0, 600, 20), color=col, label=country, legend=True, grid=True)

ax1.set_ylabel("# of Confirmed Incidents")
ax2.set_ylabel("Cases Growth Rate (%)")

# plt.tight_layout()
plt.show()
