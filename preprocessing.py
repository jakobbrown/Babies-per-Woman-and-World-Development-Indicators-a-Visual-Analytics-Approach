#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 13:00:32 2021

@author: Jake
"""

import numpy as np
import pandas as pd
import math

# setting up the world map to which the data will be applied and plotted

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
mapp = world = world[(world.pop_est>0) & (world.name!="Antarctica")] # removing antarctica for a cleaner image

# reading in all of the time series data sets for all 195 countries

birthrate = pd.read_csv('/Users/Jake/Documents/uni/Visual Analytics/coursework/Mine/gapminder data/children_per_woman_total_fertility.csv')
hdi = pd.read_csv('/Users/Jake/Documents/uni/Visual Analytics/coursework/Mine/gapminder data/hdi_human_development_index.csv')
childmortality = pd.read_csv('/Users/Jake/Documents/uni/Visual Analytics/coursework/Mine/gapminder data/child_mortality_0_5_year_olds_dying_per_1000_born.csv')
lifeexpectancy = pd.read_csv('/Users/Jake/Documents/uni/Visual Analytics/coursework/Mine/gapminder data/life_expectancy_years.csv')
foodsupply = pd.read_csv('/Users/Jake/Documents/uni/Visual Analytics/coursework/Mine/gapminder data/food_supply_kilocalories_per_person_and_day.csv')
gdppc = pd.read_csv('/Users/Jake/Documents/uni/Visual Analytics/coursework/Mine/gapminder data/gdp_per_capita_yearly_growth.csv')
population = pd.read_csv('/Users/Jake/Documents/uni/Visual Analytics/coursework/Mine/gapminder data/population_total.csv')
genderschooling = pd.read_csv('/Users/Jake/Documents/uni/Visual Analytics/coursework/Mine/gapminder data/mean_years_in_school_women_percent_men_25_to_34_years.csv')

# making a list of the countries in the map and those in the data sets, to check for necessary string matching and 
# other adjustments before merging 

countries = list(mapp['name'].unique())
countries2 = list(birthrate['country'].unique())

mismatching_names = mapp[~mapp['name'].isin(countries2)]
mismatching_names = list(mismatching_names['name'])

# lambda operations for string matching in instances where both data sets have the same country but with
# different names

mapp['name'] = mapp['name'].apply(lambda x: x.replace(' of America', '').strip())
mapp['name'] = mapp['name'].apply(lambda x: x.replace('Dem. Rep. Congo', 'Congo, Rep.').strip())
mapp['name'] = mapp['name'].apply(lambda x: x.replace('Laos', 'Lao').strip())
mapp['name'] = mapp['name'].apply(lambda x: x.replace('eSwatini', 'Eswatini').strip())
mapp['name'] = mapp['name'].apply(lambda x: x.replace('Dominican Rep.', 'Dominican Republic').strip())
mapp['name'] = mapp['name'].apply(lambda x: x.replace("Côte d'Ivoire", "Cote d'Ivoire").strip())
mapp['name'] = mapp['name'].apply(lambda x: x.replace('Central African Rep.', 'Central African Republic').strip())
mapp['name'] = mapp['name'].apply(lambda x: x.replace('Kyrgyzstan', 'Kyrgyz Republic').strip())
mapp['name'] = mapp['name'].apply(lambda x: x.replace('Solomon Is.', 'Solomon Islands').strip())
mapp['name'] = mapp['name'].apply(lambda x: x.replace('Slovakia', 'Slovak Republic').strip())
mapp['name'] = mapp['name'].apply(lambda x: x.replace('Czechia', 'Czech Republic').strip())
mapp['name'] = mapp['name'].apply(lambda x: x.replace('Bosnia and Herz.', 'Bosnia and Herzegovina').strip())


# checking for mismatching names the other way round, in the birth rate df that aren't in the map one
mismatching_names = birthrate[~birthrate['country'].isin(countries)]
mismatching_names = list(mismatching_names['country'])

# some variables were chosen not to be taken forward in the analysis, due to their data being spotty or
# not stretching back far enough to cover the important 1960s, in which the invention of the female
# contraceptive pill saw stark changes in birth rate and therefore will act as useful period to see
# if other variables changed around the same time.

datalist = [birthrate, childmortality, gdppc, lifeexpectancy, population]

# making the df from which we wil cluster the global children per woman data

mapp.rename(columns = {'name': 'country'}, inplace = True)
            
birthrateclusteringdf = pd.merge(mapp, birthrate, how = 'inner', on = 'country')
hdiclusteringdf = pd.merge(mapp, hdi, how = 'inner', on = 'country')

birthrateclusteringdf = birthrateclusteringdf.drop(['pop_est', 'continent', 'iso_a3', 'gdp_md_est', 'geometry'], axis = 1)
hdiclusteringdf = hdiclusteringdf.drop(['pop_est', 'continent', 'iso_a3', 'gdp_md_est', 'geometry'], axis = 1)


#%% creating a function that will rearrange all of the dataframes from having a column for each year 
# to having a year column and datat column, and one row for each instance of the country in a given year.


def df_sorter(df, colname):
    newdf = pd.DataFrame(columns = ['country', colname,'year'])
    numyears = df.shape[1]-1
    for idx, row in df.iterrows():
        yearcount = int(df.columns[1])
        for i in range(0, numyears):
            newdf = newdf.append({'country': row['country'], colname: row[i+1], 'year': yearcount},\
                         ignore_index = True)
            yearcount +=1
    return newdf

    
birth_rate = df_sorter(birthrate, 'birth rate')
child_mortality = df_sorter(childmortality, 'child mortality')
gdp_pc = df_sorter(gdppc, 'gdp_per_capita')
life_expectancy = df_sorter(lifeexpectancy, 'life expectancy')
population = df_sorter(population, 'population')
hdi = df_sorter(hdi, 'hdi')
birthrateclusteringdf = df_sorter(birthrateclusteringdf, 'birth rate')
hdiclusteringdf = df_sorter(hdiclusteringdf, 'hdi')

# merging the new dataframe objects. df contains all 5 features for all the countries and years that are
# available for all of them (1800 - 2018), but does not contain the geometric data as this will unnecessarily
# trim down the countries and thus the number of data rows. Geometric data will only be necessary for
# clustering and forming a chloropleth chart.

df = pd.merge(birth_rate, child_mortality, how = 'inner', on = ['country', 'year'])
df = pd.merge(df, gdp_pc, how = 'inner', on = ['country', 'year'])
df = pd.merge(df, life_expectancy, how = 'inner', on = ['country', 'year'])
df = pd.merge(df, population, how = 'inner', on = ['country', 'year'])

# clustering df has only the birth rate and the countries that have corresponding geometric coordinates
# available from the geopandas shape file we are working with. A right join is used in order to keep the 
# countries on the shape file, even if they have no birth rate or data, so that they can still be 
# displayed on the chloropleth plot with a shading indicating it is missing data. the same will be done 
# for human development index for camparative chloropleth plotting.

birthrateclusteringdf = pd.merge(birthrateclusteringdf, mapp, how = 'right', on = 'country')
hdiclusteringdf = pd.merge(hdiclusteringdf, mapp, how = 'right', on = 'country')

# the predcting df has all features but gdp per capita, a model will be trained on all 5 features up to 2018
# when gdp per capita data stops, then this predicting set will form the test set to predict future 
# gdp per capita based on the 4 other variables.

predictingdf = pd.merge(birth_rate, child_mortality, how = 'inner', on = ['country', 'year'])
predictingdf = pd.merge(predictingdf, life_expectancy, how = 'inner', on = ['country', 'year'])
predictingdf = pd.merge(predictingdf, population, how = 'inner', on = ['country', 'year'])

# creating a host of dataframes, each with a feature merged with birth rate, which can be used in
# modelling as desired. 

birthrate_childmortality = pd.merge(birth_rate, child_mortality, how = 'inner', on = ['country', 'year'])
birthrate_gdppc = pd.merge(birth_rate, gdp_pc, how = 'inner', on = ['country', 'year'])
birthrate_lifeexpectancy = pd.merge(birth_rate, life_expectancy, how = 'inner', on = ['country', 'year'])
birthrate_population = pd.merge(birth_rate, population, how = 'inner', on = ['country', 'year'])


#%% dropping small amount of rows with missing gdp values.

# for birthrate_gdppc

df1 = birthrate_gdppc[birthrate_gdppc.isna().any(axis=1)]
idx = df1.index.tolist()

birthrate_gdppc.drop(idx, inplace = True)

# and for the whole df
df1 = df[df.isna().any(axis=1)]
idx = df1.index.tolist()

df.drop(idx, inplace = True) 

#%% loading all dataframes that coul dbe useful to analysis to csv files


clusteringdf.to_csv('clusteringdf.csv')
df.to_csv('all_merged_data.csv')
predictingdf.to_csv('modelling_test_set.csv')
birthrate_childmortality.to_csv('birthrate_child_mortality.csv')
birthrategdp.to_csv('birthrate_gdp_per_capita.csv')
birthrate_lifeexpectancy.to_csv('birthrate_life_expectancy.csv')
birthrate_population.to_csv('birthrate_population.csv')
hdi.to_csv('hdi.csv')
hdiclusteringdf.to_csv('hdi_clustering.csv')


#%%

df = pd.read_csv('all_merged_data.csv', index_col = 0)
tomerge = mapp[['continent', 'country']]

df = pd.merge(df, tomerge, how = 'inner', on = 'country')
