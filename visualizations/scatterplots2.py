"""
This file produces the scatterplot of Applies vs Views
"""
import pandas as pd
import numpy as np
import altair as alt

# Prep the relevant dataset
linkedin = pd.read_csv('linkedin_df.csv')
linkedin['Company'] = linkedin['company_name']
linkedin['Salary'] = linkedin['normalized_salary'].apply(lambda x: f"${x:,.0f}")
linkedin_simple = linkedin.dropna(subset=['normalized_salary', 'views', 'applies', 'region'])
linkedin_simple = linkedin_simple[linkedin_simple['views'] <= 1500]
# Add a copy of the data with a special "All" region
all_data = linkedin_simple.copy()
all_data['region'] = 'All'
combined_data = pd.concat([linkedin_simple, all_data])
linkedin_data = combined_data.to_dict('records')

# Create the selection for the radio buttons
region_input = alt.binding_radio(
    options=sorted(linkedin_simple['region'].unique().tolist()) + ['All'],
    name='Region: '
)
region_selection = alt.param(name='region_select', value='All', bind=region_input)

# Create a filter based on the region selection
chart = alt.Chart(alt.InlineData(values=linkedin_data)).transform_filter(
    alt.datum.region == region_selection
).mark_point().encode(
    x=alt.X('views:Q', title='Views', axis=alt.Axis(grid=True)),
    y=alt.Y('applies:Q', title='Applies', axis=alt.Axis(grid=False)),
    # Use a color scale for salary ranges (0-400K)
    color=alt.Color('normalized_salary:Q',
                    title='Salary ($)',
                    scale=alt.Scale(scheme='viridis', domain=[0, 400000])),
    # Link circle size to salary
    size=alt.Size('normalized_salary:Q',
                  title='Salary ($)',
                  scale=alt.Scale(range=[20, 400])),
    # Include helpful tooltips
    tooltip=['title:N', 'Company:N', 'Salary:N', 'views:Q', 'applies:Q', 'region:N'],
    opacity=alt.value(0.6)
).properties(
    width=800,
    height=300,
    title='LinkedIn Job Postings: Views vs. Applies'
).add_params(
    region_selection
)

# Configure the chart appearance with styling from the second chart
final_chart = chart.configure_view(
    strokeWidth=0,
    continuousWidth=1000
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_legend(
    orient='bottom',
    titleFontSize=14,
    labelFontSize=12
)

final_chart.save('scatterplot2.html')