# uktraffic
Analysis &amp; Visualization of a Kaggle provided dataset (https://www.kaggle.com/daveianhickey/2000-16-traffic-flow-england-scotland-wales) of traffic accidents in the United Kingdom. 

### Getting Started 

The visualization components of this project will be heavily reliant upon Bokeh, an interactive visualization library based on d3.js. If you have the Anaconda distribution (recommended; https://anaconda.org) you can install Bokeh like so: 

`conda install bokeh`

If not, a pip install should do the trick.

`pip install bokeh`

For the Choropleth mapping component of this project, I used geopandas (http://geopandas.org), a nice GIS layer library for Python. There are other options (e.g. Fiona, Pyshp) but I opted for this one due to familiarity.

`conda install -c conda-forge geopandas`

Or...

`pip install geopandas`

The `UK_Traffic_Exploratory_Visuals.ipynb` includes all of the processing steps as well as embedded interactive plots. The `UK_Traffic_Choropleth_Map.ipynb` excludes all the processing steps and renders the choropleth maps. Due to the data intensity, most of the interactive features take very long to run or time out all together for the choropleth maps. 

There is also the ability to run Bokeh Server apps using the `interactive_exp_visuals.py` and `interactivve_choropleth.py` scripts. 

To render the exploratory visual dashboard. 

`bokeh serve --show interactive_exp_visuals.py` 

To render the interactive chroopleth maps.

`bokeh serve --show interactivve_choropleth.py`
