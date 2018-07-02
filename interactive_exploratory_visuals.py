import pandas as pd
import numpy as np
from math import pi

import yaml

from bokeh.io import (
    show, curdoc
)
from bokeh.plotting import (
    figure, Row,
    Column
)
from bokeh.palettes import (
    Blues9,
    BuPu9,
    OrRd9
)
from math import pi
from bokeh.transform import jitter
from bokeh.themes import Theme
from bokeh.models import (
    ColumnDataSource,
    ColorBar,
    LogColorMapper,
    HoverTool,
    Slider,
    Tabs,
    Panel,
    Select
)

data = "/Users/dominic/2scul4cul/uktraffic/uk_wrangled.pkl"
df = pd.read_pickle(data)
df = df.copy()

def bar_plot():

    def make_plot(var="Accident_Severity"):

            var_data = df[var].astype(str).value_counts().reset_index()
            var_data.columns = [var, "Counts"]
            var_data['perc'] = (var_data.Counts/var_data.Counts.sum())*100

            # get unique values for the variable that the data is being grouped by
            uniq_vals = [*pd.Series(var_data[var]).unique()]

            # instantiate color mapper
            mapper = LogColorMapper(palette=Blues9[::-1])

            # instantiate figure
            p = figure(y_range=uniq_vals)

            # fill figure
            p.hbar(y=var,
                   right="Counts",
                   height=0.9,
                   source=ColumnDataSource(data=var_data),
                   alpha=0.6,
                   hover_alpha=0.9,
                   fill_color= {
                       "field":"Counts",
                       "transform": mapper
                   }
                  )
            # add hover capabilities
            p.add_tools(HoverTool(tooltips = [
                ("%s" %var, "@%s" %var),
                ("Number of Accidents", "@Counts"),
                ("Percentage of Accidents", "@perc %")
            ]))

            return p

    # Create Select
    id_vars = ["Local_Authority_District", "Accident_Index",
    "Date", "LSOA_of_Accident_Location", "lad16nm",
    "poly_x", "poly_y", "xs", "ys", "st_areashape"
    ]

    # select the remaining vars that the user will be able to use
    group_vars = pd.Series(df.columns)[np.logical_not(pd.Series(df.columns).isin(id_vars))]

    # make the plot
    plot = make_plot()

    # create the select
    select = Select(value="Accident_Severity",
                    options=[*group_vars],
                    title="Select a variable to view: "
                   )

    # make an update function
    def update(attr, old, new):

        layout.children[1] = make_plot(var=select.value)

    #add interactivity
    select.on_change("value", update)

    # define layout
    layout=Column(select, plot)

    return layout

def scatter_plot():

    def make_scatter(var1="Accident_Severity", var2="Road_Type"):

        # Organise Data
        # Want var1 to be the most agg. var/or the var with the least # of classes
        # get the names of each of the variables
        name1, name2 = var1, var2

        # convert to type str
        df[var1] = df[var1].astype(str)
        df[var2] = df[var2].astype(str)

        # get the number of classes
        n_classes1 = df[var1].nunique()
        n_classes2 = df[var2].nunique()

        # eval and reassign if necessary
        if n_classes2 < n_classes1:
            var1 = name2
            var2 = name1

        # group by
        groupeddf  = (df
                      .assign(n=0)
                      .groupby([var1, var2])
                      .n
                      .count()
                      .reset_index()
                      .rename(columns={"n":"Accident_Count"})
                     )
        # calculate perc of instance against total count
        groupeddf["perc"]=(groupeddf.Accident_Count/groupeddf.Accident_Count.sum())*100

        # define the data source
        source = ColumnDataSource(data = groupeddf)

        # instantiate mapper
        mapper = LogColorMapper(palette=Blues9[::-1])

        # list of uniq values to use as a range for axis
        uniq_vals = [*df[var1].unique()]

        # instantiate the figure
        p = figure(
            plot_width=800, plot_height=600,
            title = "Accidents by %s and %s" %(var1, var2),
            y_range = uniq_vals
        )

        # fill figure
        p.circle(
            x = "Accident_Count",
            y = jitter(var1, width=0.6, range = p.y_range),
            source=source,
            alpha=0.6,
            size=30,
            hover_alpha=0.9,
            fill_color = {
                "field": "Accident_Count",
                "transform": mapper
            }
        )

        # add hover capabilities
        p.add_tools(HoverTool(tooltips=[
            ("%s" %var1,"@%s" %var1),
            ("%s" %var2,"@%s" %var2),
            ("Number of Accidents","@Accident_Count"),
            ("Percentage of Accidents","@perc")
        ]))

        return p

    # Create Select
    id_vars = ["Local_Authority_District", "Accident_Index",
    "Date", "LSOA_of_Accident_Location", "lad16nm",
    "poly_x", "poly_y", "xs", "ys", "st_areashape"
    ]

    # select the remaining vars that the user will be able to use
    group_vars = pd.Series(df.columns)[np.logical_not(pd.Series(df.columns).isin(id_vars))]

    # define select for the user to utilize
    var1_select = Select(value="Accident_Severity",
                options = [*group_vars],
                title = "Select 1st Variable to Group Data By: "
               )
    var2_select = Select(value="Road_Type",
                         options=[*group_vars],
                         title="Select 2nd Variable to Group Data By: "
                        )

    # create interactivity function
    def update_plot(attr, old, new):

        layout.children[1] = make_scatter(var1=var1_select.value, var2=var2_select.value)

    # incorporate interactivity
    var1_select.on_change("value", update_plot)
    var2_select.on_change("value", update_plot)

    # define layout
    layout = Column(Column(var1_select, var2_select), make_scatter())

    return layout

def heatmap_plot():

    def make_heatmap(var1="Accident_Severity", var2="Urban_or_Rural_Area"):

        # make sure types are category/str
        df[var1] = df[var1].astype(str)
        df[var2] = df[var2].astype(str)
        # we want the var1 to be the least granular variable
        name1, name2 = var1,var2

        # get the number of classes
        n_classes1 = df[var1].nunique()
        n_classes2 = df[var2].nunique()

        # if the num of classes in var2 is less then reassign variables
        if n_classes2 < n_classes1:
            var1 = name2
            var2 = name1

        # group the data
        groupeddf = (df
                     .assign(n=0)
                     .groupby([var1,var2])
                     .n
                     .count()
                     .reset_index()
                     .rename(columns = {"n": "Accident_Count"})
                    )

        # calculate the percentage
        groupeddf["perc"] = (groupeddf.Accident_Count/groupeddf.Accident_Count.sum())*100

        # get range of the values for the heatmap
        uniq_vals1 = [*df[var1].astype(str).unique()]
        uniq_vals2  = [*df[var2].astype(str).unique()]

        # instantiate the CDS for Bokeh
        source = ColumnDataSource(groupeddf)

        # instantiate the color mapper
        mapper = LogColorMapper(palette=BuPu9[::-1])

        # instantiate the plot
        p = figure(
            plot_width = 800, plot_height = 600,
            y_range = uniq_vals1, x_range = uniq_vals2
        )

        # specify the plot parameters
        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        p.axis.major_label_text_font_size="7pt"
        p.axis.major_label_standoff = 0
        p.xaxis.major_label_orientation = pi/3

        # fill plot
        p.rect(
            x = var2,
            y = var1,
            width = 1,
            height = 1,
            source = source,
            alpha = 0.6,
            hover_alpha = 0.9,
            fill_color = {
                "field": "Accident_Count",
                "transform": mapper
            }
        )

        p.add_tools(HoverTool(tooltips = [

            ("%s" %var1, "@%s" %var1),
            ("%s" %var2, "@%s" %var2),
            ("Number of Accidents", "@Accident_Count"),
            ("Percentage of All Acidents", "@perc %")],

                              point_policy="follow_mouse"
        ))

        return p

    # Create Select
    id_vars = ["Local_Authority_District", "Accident_Index",
    "Date", "LSOA_of_Accident_Location", "lad16nm",
    "poly_x", "poly_y", "xs", "ys", "st_areashape"
    ]

    # select the remaining vars that the user will be able to use
    group_vars = pd.Series(df.columns)[np.logical_not(pd.Series(df.columns).isin(id_vars))]

    # define select for the user to utilize
    var1_select = Select(value="Accident_Severity",
                options = [*group_vars],
                title = "Select 1st Variable to Group Data By: "
               )
    var2_select = Select(value="Road_Type",
                         options=[*group_vars],
                         title="Select 2nd Variable to Group Data By: "
                        )

    def update_heatmap(attr, old, new):

        layout.children[1] = make_heatmap(var1=var1_select.value, var2=var2_select.value)

    var1_select.on_change("value", update_heatmap)
    var2_select.on_change("value", update_heatmap)

    layout = Column(Column(var1_select, var2_select), make_heatmap())

    return layout

def adv_bar_plot():

    def make_plot(var="Accident_Severity", year=int(2012), district="Camden"):

        # filter data by year
        data = df.query("Year == %d" %int(year))

        # filter data by district
        new_data = data.query("lad16nm == '%s'" %(district))

        # group data by the variable
        var_data = new_data[var].astype(str).value_counts().reset_index()
        var_data.columns = [var, "Counts"]
        var_data['perc'] = (var_data.Counts/var_data.Counts.sum())*100

        # get unique values for the variable that the data is being grouped by
        uniq_vals = [*pd.Series(var_data[var]).unique()]

        # instantiate color mapper
        mapper = LogColorMapper(palette=Blues9[::-1])

        # instantiate figure
        p = figure(y_range=uniq_vals)

        # fill figure
        p.hbar(y=var,
               right="Counts",
               height=0.9,
               source=ColumnDataSource(data=var_data),
               alpha=0.6,
               hover_alpha=0.9,
               fill_color= {
                   "field":"Counts",
                   "transform": mapper
               }
              )
        # add hover capabilities
        p.add_tools(HoverTool(tooltips = [
            ("%s" %var, "@%s" %var),
            ("Number of Accidents", "@Counts"),
            ("Percentage of Accidents", "@perc %")
        ]))

        return p

    # Create Select
    id_vars = ["Local_Authority_District", "Accident_Index",
    "Date", "LSOA_of_Accident_Location", "lad16nm",
    "poly_x", "poly_y", "xs", "ys", "st_areashape"
    ]

    # select the remaining vars that the user will be able to use
    group_vars = pd.Series(df.columns)[np.logical_not(pd.Series(df.columns).isin(id_vars))]

    # make the plot
    plot = make_plot()

    # create the select to allow user to select the variable to veiw
    select_var = Select(value="Accident_Severity",
                    options=[*group_vars],
                    title="Select a variable to view: "
                   )

    # create select to allow user to select the year
    select_year = Select(value=str(2012),
                         options = [*df.Year.astype(str).unique()],
                         title="Select a year to view: "
                        )

    # create select to allow user to select the district
    select_district = Select(value = "Camden",
                             options = [*df.lad16nm.unique()],
                             title = "Select a district in the UK to view: "
                            )

    # make an update function
    def update(attr, old, new):

        layout.children[1] = make_plot(var=select_var.value,
                                       year=int(select_year.value),
                                       district = select_district.value
                                      )

    #add interactivity
    select_var.on_change("value", update)
    select_year.on_change("value", update)
    select_district.on_change("value", update)

    # define layout
    layout=Column(Column(select_var, select_year, select_district), plot)

    return layout

def adv_scatter_plot():

    def make_scatter(var1="Accident_Severity", var2="Road_Type", year=int(2012), district="Camden"):

        # Organise Data
        # Want var1 to be the most agg. var/or the var with the least # of classes
        # get the names of each of the variables
        name1, name2 = var1, var2

        # convert to type str
        df[var1] = df[var1].astype(str)
        df[var2] = df[var2].astype(str)

        # get the number of classes
        n_classes1 = df[var1].nunique()
        n_classes2 = df[var2].nunique()

        # eval and reassign if necessary
        if n_classes2 < n_classes1:
            var1 = name2
            var2 = name1

        # filter data by year
        data = df.query("Year == %d" %int(year))

        # filter data by district
        new_data = data.query("lad16nm == '%s'" %(district))

        # group by
        groupeddf  = (new_data
                      .assign(n=0)
                      .groupby([var1, var2])
                      .n
                      .count()
                      .reset_index()
                      .rename(columns={"n":"Accident_Count"})
                     )
        # calculate perc of instance against total count
        groupeddf["perc"]=(groupeddf.Accident_Count/groupeddf.Accident_Count.sum())*100

        # define the data source
        source = ColumnDataSource(data = groupeddf)

        # instantiate mapper
        mapper = LogColorMapper(palette=Blues9[::-1])

        # list of uniq values to use as a range for axis
        uniq_vals = [*df[var1].unique()]

        # instantiate the figure
        p = figure(
            plot_width=800, plot_height=600,
            title = "Accidents by %s and %s" %(var1, var2),
            y_range = uniq_vals
        )

        # fill figure
        p.circle(
            x = "Accident_Count",
            y = jitter(var1, width=0.6, range = p.y_range),
            source=source,
            alpha=0.6,
            size=30,
            hover_alpha=0.9,
            fill_color = {
                "field": "Accident_Count",
                "transform": mapper
            }
        )

        # add hover capabilities
        p.add_tools(HoverTool(tooltips=[
            ("%s" %var1,"@%s" %var1),
            ("%s" %var2,"@%s" %var2),
            ("Number of Accidents","@Accident_Count"),
            ("Percentage of Accidents","@perc")
        ]))

        return p

    # Create Select
    id_vars = ["Local_Authority_District", "Accident_Index",
    "Date", "LSOA_of_Accident_Location", "lad16nm",
    "poly_x", "poly_y", "xs", "ys", "st_areashape"
    ]

    # select the remaining vars that the user will be able to use
    group_vars = pd.Series(df.columns)[np.logical_not(pd.Series(df.columns).isin(id_vars))]

    # define select for the user to utilize
    var1_select = Select(value="Accident_Severity",
                options = [*group_vars],
                title = "Select 1st Variable to Group Data By: "
               )
    var2_select = Select(value="Road_Type",
                         options=[*group_vars],
                         title="Select 2nd Variable to Group Data By: "
                        )

    # create select to allow user to select the year
    select_year = Select(value=str(2012),
                         options = [*df.Year.astype(str).unique()],
                         title="Select a year to view: "
                        )

    # create select to allow user to select the district
    select_district = Select(value = "Camden",
                             options = [*df.lad16nm.unique()],
                             title = "Select a district in the UK to view: "
                            )

    # create interactivity function
    def update_plot(attr, old, new):

        layout.children[1] = make_scatter(var1=var1_select.value,
                                          var2=var2_select.value,
                                          year=select_year.value,
                                          district=select_district.value
                                         )

    # incorporate interactivity
    var1_select.on_change("value", update_plot)
    var2_select.on_change("value", update_plot)
    select_year.on_change("value", update_plot)
    select_district.on_change("value", update_plot)

    # define layout
    layout = Column(Column(var1_select, var2_select,
                           select_year, select_district),
                    make_scatter()
                   )
    return layout

def adv_heatmap_plot():

    def make_heatmap(var1="Accident_Severity", var2="Urban_or_Rural_Area", year=int(2012), district="Camden"):

        # make sure types are category/str
        df[var1] = df[var1].astype(str)
        df[var2] = df[var2].astype(str)
        # we want the var1 to be the least granular variable
        name1, name2 = var1,var2

        # get the number of classes
        n_classes1 = df[var1].nunique()
        n_classes2 = df[var2].nunique()

        # if the num of classes in var2 is less then reassign variables
        if n_classes2 < n_classes1:
            var1 = name2
            var2 = name1

        # filter data by year
        data = df.query("Year == %d" %int(year))

        # filter data by district
        new_data = data.query("lad16nm == '%s'" %(district))

        # group the data
        groupeddf = (df
                     .assign(n=0)
                     .groupby([var1,var2])
                     .n
                     .count()
                     .reset_index()
                     .rename(columns = {"n": "Accident_Count"})
                    )

        # calculate the percentage
        groupeddf["perc"] = (groupeddf.Accident_Count/groupeddf.Accident_Count.sum())*100

        # get range of the values for the heatmap
        uniq_vals1 = [*df[var1].astype(str).unique()]
        uniq_vals2  = [*df[var2].astype(str).unique()]

        # instantiate the CDS for Bokeh
        source = ColumnDataSource(groupeddf)

        # instantiate the color mapper
        mapper = LogColorMapper(palette=BuPu9[::-1])

        # instantiate the plot
        p = figure(
            plot_width = 800, plot_height = 600,
            y_range = uniq_vals1, x_range = uniq_vals2
        )

        # specify the plot parameters
        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        p.axis.major_label_text_font_size="7pt"
        p.axis.major_label_standoff = 0
        p.xaxis.major_label_orientation = pi/3

        # fill plot
        p.rect(
            x = var2,
            y = var1,
            width = 1,
            height = 1,
            source = source,
            alpha = 0.6,
            hover_alpha = 0.9,
            fill_color = {
                "field": "Accident_Count",
                "transform": mapper
            }
        )

        p.add_tools(HoverTool(tooltips = [

            ("%s" %var1, "@%s" %var1),
            ("%s" %var2, "@%s" %var2),
            ("Number of Accidents", "@Accident_Count"),
            ("Percentage of All Acidents", "@perc %")],

                              point_policy="follow_mouse"
        ))

        return p

    # Create Select
    id_vars = ["Local_Authority_District", "Accident_Index",
    "Date", "LSOA_of_Accident_Location", "lad16nm",
    "poly_x", "poly_y", "xs", "ys", "st_areashape"
    ]

    # select the remaining vars that the user will be able to use
    group_vars = pd.Series(df.columns)[np.logical_not(pd.Series(df.columns).isin(id_vars))]

    # define select for the user to utilize
    var1_select = Select(value="Accident_Severity",
                options = [*group_vars],
                title = "Select 1st Variable to Group Data By: "
               )
    var2_select = Select(value="Road_Type",
                         options=[*group_vars],
                         title="Select 2nd Variable to Group Data By: "
                        )

    # create select to allow user to select the year
    select_year = Select(value=str(2012),
                         options = [*df.Year.astype(str).unique()],
                         title="Select a year to view: "
                        )

    # create select to allow user to select the district
    select_district = Select(value = "Camden",
                             options = [*df.lad16nm.unique()],
                             title = "Select a district in the UK to view: "
                            )

    def update_plot(attr, old, new):

        layout.children[1] = make_heatmap(var1=var1_select.value,
                                          var2=var2_select.value,
                                          year=select_year.value,
                                          district=select_district.value
                                         )

    # incorporate interactivity
    var1_select.on_change("value", update_plot)
    var2_select.on_change("value", update_plot)
    select_year.on_change("value", update_plot)
    select_district.on_change("value", update_plot)

    # define layout
    layout = Column(Column(var1_select, var2_select,
                           select_year, select_district),
                    make_heatmap()
                   )
    return layout

layout = Tabs(tabs=[
    Panel(child=bar_plot(),title="Bar Plot"),
    Panel(child=scatter_plot(),title="Scatter Plot"),
    Panel(child=heatmap_plot(),title="Heatmap Plot"),
    Panel(child=adv_bar_plot(),title="Advanced Bar Plot"),
    Panel(child=adv_scatter_plot(),title="Advanced Scatter Plot"),
    Panel(child=adv_heatmap_plot(),title="Advanced Heatmap Plot")
])

curdoc().add_root(layout)
