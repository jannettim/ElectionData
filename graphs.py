from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure
from analysis import get_efficiency_gap
import pandas as pd
import os


gaps = get_efficiency_gap("federal")[['State', 'Year', 'gap']]
gaps = gaps.loc[gaps.Year >= 1972]
state_abbr = pd.read_excel("/home/matt/GitRepos/ElectionData/data/StateAbbr_Name_Lookup.xlsx")

# gaps = gaps.merge(state_abbr, on=["State"], how="inner")


gaps_year_df = gaps.groupby("Year", as_index=False).mean()

gap_year = ColumnDataSource(data=dict(year=gaps_year_df["Year"].tolist(),
                                      gap=gaps_year_df["gap"].tolist()))

state_year_gaps = ColumnDataSource(data=dict(state=gaps["State"].tolist(),
                                             year=gaps["Year"].tolist(),
                                             gap=gaps["gap"].tolist()))#,
                                             #state_abbr=gaps["State_Abbr"].tolist()))

# p = figure(plot_width=1500, plot_height=1500)
p = figure()

# p.scatter(x="year", y="gap", source=state_year_gaps)
#
# p.add_layout(LabelSet(x='year', y='gap', text='state_abbr', level='glyph', x_offset=5, y_offset=5, source=state_year_gaps))
# show(p)


p.line(x="year", y="gap", source=gap_year)

show(p)

gaps = gaps.loc[(gaps["Year"] >= 2000) & (gaps["Year"] <= 2010)]
gaps.groupby("State", as_index=False).mean().to_csv('test.csv')
os.system("xdg-open test.csv")