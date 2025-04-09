"""
This file produces the Map visualization
"""
import pandas as pd
import altair as alt

# Prep the relevant dataset
linkedin = pd.read_csv('linkedin_df.csv')
linkedin['Company'] = linkedin['company_name']
linkedin['Salary'] = linkedin['normalized_salary'].apply(lambda x: f"${x:,.0f}")
linkedin_simple = linkedin.dropna(subset=['normalized_salary', 'views', 'applies', 'region'])
linkedin_simple = linkedin_simple[linkedin_simple['views'] <= 1500]
linkedin_data = linkedin_simple.to_dict('records')

# Define region multi-select using selection_point (Altair 5+ compatible)
region_select = alt.selection_point(fields=['region'], toggle=True, bind='legend', name='RegionSelector')

# Define salary brush
salary_brush = alt.selection_interval(encodings=['x'], name='brush')

# Left chart: Salary vs Views (highlight selected regions)
salary_vs_views = alt.Chart(alt.InlineData(values=linkedin_data)).mark_point(size=100).encode(
    x=alt.X('normalized_salary:Q', title='Salary', axis=alt.Axis(grid=True)),
    y=alt.Y('views:Q', title='Views', axis=alt.Axis(grid=False)),
    color=alt.Color('region:N', title='Region', legend=alt.Legend(orient='bottom')),
    opacity=alt.condition(region_select, alt.value(0.6), alt.value(0.05)),
    tooltip=['title:N', 'Company:N', 'Salary:N']
).add_params(
    salary_brush,
    region_select
).properties(
    width=500,
    height=400,
    title='Salary vs. Views'
)

# Right chart: Salary vs Applies (filtered by brush, highlight selected regions)
salary_vs_applies = alt.Chart(alt.InlineData(values=linkedin_data)).mark_circle(size=100).encode(
    x=alt.X('normalized_salary:Q', title='Salary', axis=alt.Axis(grid=True)),
    y=alt.Y('applies:Q', title='Applies', axis=alt.Axis(grid=False)),
    color=alt.Color('region:N', title='Region', legend=alt.Legend(orient='bottom')),
    opacity=alt.condition(region_select, alt.value(0.6), alt.value(0.05)),
    tooltip=['title:N', 'Company:N', 'Salary:N']
).transform_filter(
    salary_brush
).add_params(
    region_select
).properties(
    width=500,
    height=400,
    title='Salary vs. Applies'
)

# Side-by-side layout centered in a container
linked_scatterplots = alt.hconcat(salary_vs_views, salary_vs_applies).configure_view(
    continuousWidth=1000
).configure_legend(
    orient='bottom'
)

# Export chart as HTML
linked_scatterplots.save('scatterplots.html')