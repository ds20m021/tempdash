# Dashboard: World Temperatures
This dashboard shows the temperature of differente countries over time. [Data](https://www.kaggle.com/berkeleyearth/climate-change-earth-surface-temperature-data) on a country level is used

## Controlls
### Slider
A slider is used to controll the current year
#### Country selection
A dropdown is used to select the country to display details

## Diagrams
### Choropleth plot
The map displays the avarage temperature of each country in the selected year
### Violin plot
Displays the temperature distribution of the countries available for selection in the selected year
### Temperature over the year
Plot that displays the temperature change of the selected country over one year, in comparison with the next 3 years
### Tempeature with prediciton
Comparison of world avarage temperature with a prediction for the next 10 years with those of the selected country, actual future temperatures are displayed as well
Predicitons are taken from [this service](https://github.com/ds20mm008/Viz-Model) hosted on [azure](https://ds20m008-autopublisher-project.azurewebsites.net/)
### Animated change of prediction
An animation shows how the prediction changes when the time is moved forward
