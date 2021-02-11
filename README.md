# Visual Analytics project with World Development Indicators

This project looks to use spatio-temporal data to exmaine from multiple angles the relationships between World Development Indicators (WDIs), specifically 'Babies per Woman', aka the fertility rate of a country in a given year. 

The project is 3-fold: A time-series analysis is conducted, using Tableau and python visualisation libraries to look at and identify relationships betweeen several key WDIs over 2 centuries, as well as think of possible explanations for observable flucuations and trends at different points in time by linking visulisations with previous literature (see report file).

Next, a k-means clustering model was built and optimised via silhouette analysis, settling on 3 clusters to group together countries in present day in relation to their Human Development Index (HDI) and babies per woman. These clustering results were then visulised via choropleth mapping, in order to observe the relationship between the two, and to corroborate the rationale for the 3 and final part of the study, a predictive regression model built with HDI as the target variable, and babies per woman as one of the key predictors. 

Results were strong, and thus could be used as a tool for monitoring and assessment of development needs in different areas of the world. Additional steps and visualisations taken in the programming and modelling can be seen in the supporting notebook.


Data was obtained from https://www.gapminder.org/.
