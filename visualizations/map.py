"""
This file produces the file: folium_map.html
"""
import folium
import pandas as pd
import geopandas as gpd
from folium import Choropleth, LayerControl, GeoJsonTooltip, GeoJsonPopup
from ast import literal_eval  # if your skills column is stored as a string

# ===================== Load and Process COUNTY Data ===================== #
county = gpd.read_file('ne_10m_admin_2_counties')
county['county_fips'] = [float(f[2:]) for f in county.FIPS]

df = pd.read_csv('linkedin_df.csv')
df['skill_name'] = df['skill_name'].apply(literal_eval)
df_county_med = df.groupby('fips').median(numeric_only=True).reset_index()[['fips','normalized_salary']].rename(columns={'normalized_salary':'median_salary'})
df_county_mean = df.groupby('fips').mean(numeric_only=True).reset_index()[['fips','normalized_salary']].rename(columns={'normalized_salary':'mean_salary'})
df_county = pd.merge(df_county_med,df_county_mean,on='fips')
df_county['median_salary_display'] = df_county['median_salary'].apply(lambda x: f"${x:,.0f}")
df_county['mean_salary_display'] = df_county['mean_salary'].apply(lambda x: f"${x:,.0f}")
usa_county = pd.merge(county, df_county, left_on='county_fips', right_on='fips', how='left')
usa_county.dropna(subset=['mean_salary'],inplace=True)

# ===================== Tool Tip County ===================== #
sector = df.groupby(['fips', 'Sector']).count()[['job_id']].rename(columns={'job_id': 'job_count'})

sector_top = (
    sector.groupby('fips', group_keys=False)
          .apply(lambda x: x.sort_values('job_count', ascending=False).head(1))
          .reset_index()
).rename(columns={'Sector':'top_sector'})

total_jobs = df.groupby(['fips']).count()[['job_id']].rename(columns={'job_id': 'total_jobs'})

tooltip_county = pd.merge(total_jobs, sector_top, on='fips')
tooltip_county['pct_sector'] = tooltip_county.job_count / tooltip_county.total_jobs
tooltip_county['pct_sector_display'] = tooltip_county['pct_sector'].apply(lambda x: f"{x*100:.0f}%")

exploded = df.explode('skill_name')
skill_counts = exploded.groupby(['fips', 'skill_name']).size().reset_index(name='count')
top_3_skills = skill_counts.sort_values(['fips', 'count'], ascending=[True, False]).groupby('fips').head(3)
top_skills_county = top_3_skills.groupby('fips')['skill_name'].apply(list).reset_index(name='top_skills')
tooltip_county = pd.merge(top_skills_county, tooltip_county, on='fips')

usa_county = pd.merge(usa_county, tooltip_county, on='fips', how='left')

# ===================== Load and Process STATE Data ===================== #
state = gpd.read_file('ne_110m_admin_1_states_provinces')
state['fips_state'] = [int(string[2:]) for string in state.fips]

df_state_med = df.groupby('fips_state').median(numeric_only=True).reset_index()[['fips_state','normalized_salary']].rename(columns={'normalized_salary':'median_salary'})
df_state_mean = df.groupby('fips_state').mean(numeric_only=True).reset_index()[['fips_state','normalized_salary']].rename(columns={'normalized_salary':'mean_salary'})
df_state = pd.merge(df_state_med,df_state_mean,on='fips_state')
df_state['median_salary_display'] = df_state['median_salary'].apply(lambda x: f"${x:,.0f}")
df_state['mean_salary_display'] = df_state['mean_salary'].apply(lambda x: f"${x:,.0f}")
usa_state = pd.merge(state, df_state, on='fips_state', how='left')
usa_state.dropna(subset=['mean_salary'],inplace=True)

# ===================== Tool Tip State ===================== #
sector = df.groupby(['fips_state', 'Sector']).count()[['job_id']].rename(columns={'job_id': 'job_count'})

sector_top = (
    sector.groupby('fips_state', group_keys=False)
          .apply(lambda x: x.sort_values('job_count', ascending=False).head(1))
          .reset_index()
).rename(columns={'Sector':'top_sector'})

total_jobs = df.groupby(['fips_state']).count()[['job_id']].rename(columns={'job_id': 'total_jobs'})

tooltip_state = pd.merge(total_jobs, sector_top, on='fips_state')
tooltip_state['pct_sector'] = tooltip_state.job_count / tooltip_state.total_jobs
tooltip_state['pct_sector_display'] = tooltip_state['pct_sector'].apply(lambda x: f"{x*100:.1f}%")

exploded = df.explode('skill_name')
skill_counts = exploded.groupby(['fips_state', 'skill_name']).size().reset_index(name='count')
top_3_skills = skill_counts.sort_values(['fips_state', 'count'], ascending=[True, False]).groupby('fips_state').head(3)
top_skills_state = top_3_skills.groupby('fips_state')['skill_name'].apply(list).reset_index(name='top_skills')
tooltip_state = pd.merge(top_skills_state, tooltip_state, on='fips_state')

usa_state = pd.merge(usa_state, tooltip_state, on='fips_state', how='left')


# ===================== Base Map ===================== #
m = folium.Map(
    location=[37.8, -96],
    zoom_start=4,
    tiles=None,
    max_bounds=True,
    min_zoom=3,
    max_zoom=7,
    min_lon = -96-50,
    max_lon = -96+50,
    min_lat = 37.8-30,
    max_lat = 37.8+30,
)
folium.TileLayer('CartoDB positron', min_zoom=2).add_to(m)

# ===================== County Layer ===================== #
county_bins = [0, 100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000]
county_choropleth = Choropleth(
    geo_data=usa_county,
    name='County Salary Range',
    data=usa_county,
    columns=['county_fips', 'mean_salary'],
    key_on='feature.properties.county_fips',
    fill_color='plasma',
    fill_opacity=0.5,
    line_opacity=0.2,
    bins=county_bins,
    legend_name='County Normalized Salary (USD)',
    nan_fill_color='lightgrey',
    highlight=True
).add_to(m)

GeoJsonTooltip(
    fields=['NAME', 'mean_salary_display'],
    aliases=['County', 'Average Salary'],
    style="""
        font-size: 14px;  
    """,
    localize=True,
    sticky=False,
    labels=True
).add_to(county_choropleth.geojson)
GeoJsonPopup(
    fields=['NAME', 'mean_salary_display', 'median_salary_display', 'total_jobs', 'top_sector', 'pct_sector_display', 'top_skills'],
    aliases=['County', 'Mean Salary', 'Median Salary', 'Total Jobs', 'Top Sector', '% Jobs', 'Top Skills'],
    localize=True,
    max_width=450,
    style="""
        font-size: 12px;  
    """
).add_to(county_choropleth.geojson)

# ===================== State Layer ===================== #
state_bins = [0, 40000, 60000, 80000, 100000, 120000, 150000]
state_choropleth = Choropleth(
    geo_data=usa_state,
    name='State Salary Range',
    data=usa_state,
    columns=['fips_state', 'mean_salary'],
    key_on='feature.properties.fips_state',
    fill_color='viridis',
    fill_opacity=0.5,
    line_opacity=0.2,
    bins=state_bins,
    legend_name='State Normalized Salary (USD)',
    nan_fill_color='lightgrey',
    highlight=True
).add_to(m)

GeoJsonTooltip(
    fields=['name', 'mean_salary_display'],
    aliases=['State', 'Average Salary'],
    localize=True,
    sticky=False,
    labels=True
).add_to(state_choropleth.geojson)
GeoJsonPopup(
    fields=['name', 'mean_salary_display', 'median_salary_display', 'total_jobs', 'top_sector', 'pct_sector_display', 'top_skills'],
    aliases=['State', 'Mean Salary', 'Median Salary', 'Total Jobs', 'Top Sector', '% Jobs', 'Top Skills'],
    localize=True,
    max_width=450,
    style="""
        font-size: 12px;  
    """
).add_to(state_choropleth.geojson)

# ===================== Layer Controls and Fit Bounds ===================== #
LayerControl().add_to(m)
m.fit_bounds([[24.396308, -125.0], [49.384358, -66.93457]])

# Show the map
m.save('folium_map.html')
