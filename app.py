import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Global Population Visualisation",
    page_icon="🌍",
    layout="wide"
)

DATA_URL = (
    "https://ourworldindata.org/grapher/population-unwpp.csv"
    "?v=1&csvType=full&useColumnShortNames=false"
)

CONTINENTS = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania"]

@st.cache_data(show_spinner="Loading population dataset...")
def load_data():
    df = pd.read_csv(DATA_URL, storage_options={"User-Agent": "Scientific Visualisation student project"})
    df.columns = [str(c).strip() for c in df.columns]

    required = {"Entity", "Year"}
    if not required.issubset(df.columns):
        raise ValueError(f"Dataset is missing expected columns. Columns found: {list(df.columns)}")

    value_candidates = [
        c for c in df.columns
        if c not in {"Entity", "Code", "Year"} and "population" in c.lower()
    ]
    if not value_candidates:
        raise ValueError(f"Could not identify the population column. Columns found: {list(df.columns)}")

    value_col = value_candidates[0]
    df = df.rename(columns={value_col: "Population"})
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Population"] = pd.to_numeric(df["Population"], errors="coerce")
    df = df.dropna(subset=["Entity", "Year", "Population"])
    df["Year"] = df["Year"].astype(int)
    df = df[df["Population"] > 0].copy()
    return df

st.title("🌍 Global Population Growth and Distribution")
st.caption("JIE42403 – Scientific Visualisation | Interactive Streamlit report")

with st.expander("About this project and data source"):
    st.write(
        "This application explores global population trends, compares continental "
        "population patterns, and examines how population is distributed among countries."
    )
    st.markdown(
        "**Dataset:** Population 1950–2023, processed by Our World in Data from "
        "the United Nations World Population Prospects 2024."
    )
    st.markdown(
        "[Open dataset and metadata](https://ourworldindata.org/grapher/population-unwpp)"
    )
    st.caption("Population is measured in people. Cite Our World in Data and the UN World Population Prospects 2024.")

try:
    df = load_data()
except Exception as e:
    st.error("The dataset could not be loaded. Check your internet connection and try again.")
    st.exception(e)
    st.stop()

year_min = int(df["Year"].min())
year_max = int(df["Year"].max())
years = sorted(df["Year"].unique().tolist())

st.sidebar.header("Dashboard controls")
selected_year = st.sidebar.select_slider(
    "Select year for country comparison",
    options=years,
    value=year_max
)
st.sidebar.caption(f"Dataset year range: {year_min}–{year_max}")

world = df[df["Entity"].str.lower().eq("world")].sort_values("Year")
if world.empty:
    st.error("The dataset does not contain a 'World' aggregate row.")
    st.stop()

latest_world = world[world["Year"] == year_max]["Population"]
latest_world_value = float(latest_world.iloc[-1]) if not latest_world.empty else float("nan")
first_world_value = float(world.iloc[0]["Population"])
growth_pct = ((latest_world_value - first_world_value) / first_world_value * 100) if first_world_value else float("nan")

tab1, tab2, tab3 = st.tabs([
    "Page 1 — Global Trend",
    "Page 2 — Continental Comparison",
    "Page 3 — Country Distribution"
])

with tab1:
    st.header("Objective 1: Examine global population growth over time")
    st.write("Objective: Identify the long-term trend in the world's population and quantify the overall change across the available period.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Latest available year", f"{year_max}")
    c2.metric("World population in latest year", f"{latest_world_value / 1e9:.2f} billion")
    c3.metric(f"Change since {year_min}", f"{growth_pct:.1f}%")

    fig1 = px.line(
        world, x="Year", y="Population",
        title="World Population Over Time",
        labels={"Year": "Year", "Population": "Population (people)"},
        markers=True
    )
    fig1.update_layout(yaxis_tickformat=",.0f")
    st.plotly_chart(fig1, use_container_width=True)

    world["Population_Billions"] = world["Population"] / 1e9
    fig2 = px.area(
        world, x="Year", y="Population_Billions",
        title="Cumulative Scale of World Population",
        labels={"Year": "Year", "Population_Billions": "Population (billions)"}
    )
    st.plotly_chart(fig2, use_container_width=True)

    world["Annual_Change_Millions"] = world["Population"].diff() / 1e6
    fig3 = px.bar(
        world.dropna(subset=["Annual_Change_Millions"]),
        x="Year", y="Annual_Change_Millions",
        title="Year-to-Year Change in World Population",
        labels={"Year": "Year", "Annual_Change_Millions": "Change (millions of people)"}
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Summary of Key Findings")
    st.write(
        "World population increased from approximately 2.5 billion in 1950 to over 8 billion in 2023.\nAnnual population additions changed over time.\nThe annual increase generally declined in recent years, although total population continued to grow."
    )

with tab2:
    st.header("Objective 2: Compare population patterns across continents")
    st.write("Objective: Compare the size and long-term development of populations in major world regions.")

    continent_df = df[df["Entity"].isin(CONTINENTS)].copy()
    if continent_df.empty:
        st.warning(
            "The selected source did not provide continent rows in the expected format. "
            "The global and country pages can still work, but the dataset needs a continent mapping or a different source for this page."
        )
    else:
        continent_latest = continent_df[continent_df["Year"] == year_max].sort_values("Population", ascending=False)
        total_continent_population = continent_latest["Population"].sum()
        top_continent = continent_latest.iloc[0] if not continent_latest.empty else None

        c1, c2, c3 = st.columns(3)
        c1.metric("Continents available", f"{continent_df['Entity'].nunique()}")
        c2.metric("Largest continent in latest year", top_continent["Entity"] if top_continent is not None else "N/A")
        c3.metric("Largest continent population", f"{top_continent['Population'] / 1e9:.2f} billion" if top_continent is not None else "N/A")

        fig4 = px.line(
            continent_df, x="Year", y="Population", color="Entity",
            title="Population Trends by Continent",
            labels={"Year": "Year", "Population": "Population (people)", "Entity": "Continent"}
        )
        fig4.update_layout(yaxis_tickformat=",.0f")
        st.plotly_chart(fig4, use_container_width=True)

        fig5 = px.bar(
            continent_latest, x="Entity", y="Population", color="Entity",
            title=f"Population by Continent in {year_max}",
            labels={"Entity": "Continent", "Population": "Population (people)"}
        )
        fig5.update_layout(yaxis_tickformat=",.0f", showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)

        continent_pivot = continent_df.pivot_table(index="Year", columns="Entity", values="Population", aggfunc="first")
        continent_share = continent_pivot.div(continent_pivot.sum(axis=1), axis=0) * 100
        share_long = continent_share.reset_index().melt(id_vars="Year", var_name="Continent", value_name="Share")
        fig6 = px.area(
            share_long, x="Year", y="Share", color="Continent",
            title="Share of Combined Continent Population Over Time",
            labels={"Year": "Year", "Share": "Share (%)", "Continent": "Continent"}
        )
        st.plotly_chart(fig6, use_container_width=True)

        st.subheader("Summary of Key Findings")
        st.write(
            "Asia has the largest population among the continents."
            "Africa experienced strong population growth."
            "Africa's share of the combined continental population increased over time."
        )

with tab3:
    st.header("Objective 3: Explore differences in population between countries")
    st.write("Objective: Identify the most populous countries and examine the geographic distribution of population.")

    country_year = df[df["Year"] == int(selected_year)].copy()
    if "Code" in country_year.columns:
        country_year = country_year[country_year["Code"].notna()]
        country_year = country_year[country_year["Code"].astype(str).str.fullmatch(r"[A-Z]{3}", na=False)]
        country_year = country_year[~country_year["Entity"].str.lower().isin(["world"] + [c.lower() for c in CONTINENTS])]
    else:
        st.warning("The dataset has no country code column; map visualization may not be available.")

    country_year = country_year.sort_values("Population", ascending=False)
    c1, c2, c3 = st.columns(3)
    c1.metric("Countries/areas available", f"{country_year['Entity'].nunique()}")
    if not country_year.empty:
        c2.metric("Most populous country/area", country_year.iloc[0]["Entity"])
        c3.metric("Population of largest", f"{country_year.iloc[0]['Population'] / 1e6:,.1f} million")

    top10 = country_year.head(10)
    fig7 = px.bar(
        top10.sort_values("Population"), x="Population", y="Entity",
        orientation="h", title=f"Top 10 Most Populous Countries/Areas ({selected_year})",
        labels={"Population": "Population (people)", "Entity": "Country/area"}
    )
    fig7.update_layout(xaxis_tickformat=",.0f")
    st.plotly_chart(fig7, use_container_width=True)

    if "Code" in country_year.columns and not country_year.empty:
        fig8 = px.choropleth(
            country_year, locations="Code", color="Population",
            hover_name="Entity", hover_data={"Population": ":,.0f", "Code": True},
            title=f"Geographic Distribution of Population ({selected_year})",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig8, use_container_width=True)
    else:
        st.info("The map requires valid three-letter country codes in the dataset.")

    top10_pie = top10.copy()
    fig9 = px.pie(
        top10_pie, names="Entity", values="Population",
        title=f"Population Share Among the Top 10 Countries/Areas ({selected_year})"
    )
    st.plotly_chart(fig9, use_container_width=True)

    st.subheader("Summary of Key Findings")
    st.write(
        "India and China are the two largest country entries in 2023."
        "The United States is the third-largest entry."
        "The map and pie chart show geographic distribution and population differences among the top ten entries."
    )

st.divider()
st.caption(
    "Source: Our World in Data, Population 1950–2023, based on United Nations World Population Prospects 2024. "
    "Population values are estimates and should be interpreted in light of the source's methodology."
)
