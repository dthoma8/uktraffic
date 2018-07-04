import pandas as  pd
import numpy as np

from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.palettes import OrRd9
from bokeh.tile_providers import CARTODBPOSITRON

from bokeh.models import (
    ColumnDataSource,
    LogColorMapper,
    HoverTool,
    ColorBar,
    Select,
    Column
)

df = pd.read_pickle("./uk_wrangled.pkl")

def make_data(var="Accident_Count", id_var="lad16nm"):

    if var == "Accident_Count":

        accident_data = (df["lad16nm"]
                         .value_counts()
                         .reset_index()
                         .rename(columns={"lad16nm":"Accident_Count",
                                          "index":"lad16nm"}
                                )
                         .merge(df[["lad16nm", "xs", "ys"]])
                         .drop_duplicates(subset=["lad16nm"])
                         .reset_index(drop=True)
                        )
    else:

        accident_data = (df
                         .dropna(subset=[id_var], axis=0)
                         .assign(n=0)
                         .groupby([id_var, var])
                         .n
                         .count()
                         .reset_index()
                         .rename(columns = {"n":"Accident_Count"})
                         .merge(df[[id_var,"poly_x", "poly_y"]])
                         .drop_duplicates(subset=[id_var, var])
                         .sort_values("Accident_Count",ascending=False)
                         .reset_index(drop=True)
                        )

    return accident_data

def make_map(accident_data=make_data()):

    # create the mapper to color the jurisdictions on the map
    mapper = LogColorMapper(palette=OrRd9[::-1])

    # instantiate the map
    p = figure(x_range=(-630000, 162000),
               y_range=(6500000, 8600000),

               # converts to lats/longs
               x_axis_type="mercator",
               y_axis_type="mercator",
               plot_height=1200,
               plot_width=1000,
               output_backend="webgl"

            )
    # add tile
    p.grid.grid_line_color = None
    p.axis.visible = False
    p.add_tile(CARTODBPOSITRON)

    # fill plot
    p.patches(xs="xs", ys="ys",
              fill_color = {"field":"Accident_Count",
                            "transform":mapper
                           },
              fill_alpha=0.9,
              line_color=None,
              source=ColumnDataSource(data=accident_data)
             )

    # add in hover capabilities for user
    p.add_tools(HoverTool(tooltips = [
        ("Local Authority District ID", "@lad16nm"),
        ("Accident_Count", "@Accident_Count")
    ]))

    # add in color bar to describe magnitude
    p.add_layout(ColorBar(color_mapper=mapper,
                          title = "Number of Accidents"
                         ),
                "right")

    return p

# Create Select
# create list of non-visual vars
id_vars = ["Local_Authority_District", "Accident_Index",
   "Date", "LSOA_of_Accident_Location", "lad16nm",
   "poly_x", "poly_y", "xs", "ys", "st_areashape"
  ]
 # define visual vars
 # select the remaining vars that the user will be able to use
group_vars = [*pd.Series(df.columns)[np.logical_not(pd.Series(df.columns).isin(id_vars))]]
group_vars.append("Accident_Count")

# define variable select
var_select = Select(value="Accident_Count",
                    options=[*group_vars],
                    title="Select a variable to view: "
)

# create function fro interactivity
def update(attr, old, new):

    layout.children[1] = make_map(accident_data=make_map(var=var_select.value))

# add in interactivity
var_select.on_change('value', update)

# define layout
layout = Column(var_select, make_map())

curdoc().add_root(layout)
