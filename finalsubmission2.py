import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pycountry



# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(

    page_title="Global Book Industry Analysis",

    layout="wide"

)



# ==========================================
# LOAD BOOK DATA
# ==========================================

@st.cache_data
def load_books():

    booksread = pd.read_excel(
        "average_books_read_per_year_by_country_2026.xlsx"
    )


    country_mapping = {

        "Russia": "Russian Federation",

        "Taiwan": "Taiwan, Province of China",

        "Iran": "Iran, Islamic Republic of",

        "Turkey": "Türkiye",

        "South Korea": "Korea, Republic of",

        "Vietnam": "Viet Nam",

        "Venezuela": "Venezuela, Bolivarian Republic of",

        "Macau": "Macao",

        "Moldova": "Moldova, Republic of",

        "Syria": "Syrian Arab Republic",

        "Brunei": "Brunei Darussalam"

    }


    booksread["country"] = (

        booksread["country"]

        .replace(country_mapping)

    )


    return booksread





booksread = load_books()





# ==========================================
# LOAD GDP DATA
# ==========================================

@st.cache_data
def load_gdp():

    gdp = pd.read_excel(

        "GDP.xlsx"

    )


    books = pd.read_excel(

        "average_books_read_per_year_by_country_2026.xlsx"

    )



    # Clean column names

    gdp.columns = (

        gdp.columns

        .str.strip()

        .str.lower()

    )


    books.columns = (

        books.columns

        .str.strip()

        .str.lower()

    )



    country_fix = {

        "United States": "USA",

        "United Kingdom": "UK",

        "Korea, Republic of": "South Korea",

        "Russian Federation": "Russia",

        "Viet Nam": "Vietnam",

        "Iran, Islamic Republic of": "Iran",

        "Taiwan, Province of China": "Taiwan",

        "Macao": "Macau",

        "Brunei Darussalam": "Brunei",

        "Venezuela, Bolivarian Republic of": "Venezuela",

        "Moldova, Republic of": "Moldova",

        "Syrian Arab Republic": "Syria"

    }



    gdp["country"] = (

        gdp["country"]

        .str.strip()

        .replace(country_fix)

    )



    books["country"] = (

        books["country"]

        .str.strip()

        .replace(country_fix)

    )



    df = pd.merge(

        gdp,

        books,

        on="country",

        how="inner"

    )



    df["booksreadannually_2024"] = (

        df["booksreadannually_2024"]

        .fillna(0)

    )


    return df





gdp_data = load_gdp()

# ==========================================
# LOAD GENRE DATA
# ==========================================

@st.cache_data
def load_genres():

    booksgenre = pd.read_excel(
        "best_selling_books_2.xlsx"
    )

    totalsalebygenre = (

        booksgenre
        .groupby("Genre")["Volume Sales"]
        .sum()
        .reset_index()

    )

    top10genres = (

        totalsalebygenre
        .sort_values(
            by="Volume Sales",
            ascending=False
        )
        .head(10)

    )

    return top10genres


genre_data = load_genres()



# ==========================================
# ISO COUNTRY CODE
# ==========================================

def get_iso3(country_name):

    try:

        return pycountry.countries.lookup(

            country_name

        ).alpha_3


    except:

        return None





booksread["iso_alpha"] = (

    booksread["country"]

    .apply(get_iso3)

)





numeric_columns = (

    booksread

    .select_dtypes(

        include="number"

    )

    .columns

    .tolist()

)

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:


    st.header(
        "Navigation"
    )


    st.info(
        "Book Market Analysis"
    )


    st.divider()



    metric_labels = {

        "BooksReadAnnually_2024":
        "Annual Average Books Read",


        "HoursSpentReadingPerYear_2024":
        "Annual Average Reading Hours Spent"

    }



    available_metrics = [

        col

        for col in metric_labels.keys()

        if col in numeric_columns

    ]



    selected_metric_label = st.selectbox(

        "📊 Select Metric",

        [

            metric_labels[col]

            for col in available_metrics

        ]

    )



    selected_metric = {

        metric_labels[col]:

        col

        for col in available_metrics

    }[selected_metric_label]



    selected_color = st.selectbox(

        "🎨 Select Color Scheme",

        [

            "YlOrRd",

            "Viridis",

            "Plasma",

            "Cividis"

        ]

    )





# ==========================================
# TITLE
# ==========================================

st.title(

    "📚 Global Book Market Analysis"

)

st.markdown("""
This dashboard visualizes global reading patterns, and the evaluation of market entry potential and product lines.

A map and a bar chart are used to visualize the global reading patterns across different countries. From that, book publishiers can gain an insight into how customer interest and demand varied significantly across countries.

For the map, please use the controls in the sidebar to switch between reading metrics and color schemes.

The market entry potential is evaluated under the influence of economic and cultural indicators. It is depicted by a mixed chart to examine whether highest GDP countries have greater market entry potential.

Finally, product lines are assessed based on total sales among book genres with a 3D pie chart


""")

st.divider()





# ==========================================
# KPI SECTION
# ==========================================

k1, k2, k3 = st.columns(3)



with k1:

    st.metric(

        "Countries Surveyed",

        len(booksread)

    )



with k2:

    st.metric(

        "Annual Average Books Read",

        round(

            booksread[

                "BooksReadAnnually_2024"

            ]

            .mean(),

            1

        )

    )



with k3:

    st.metric(

        "Annual Average Reading Hours",

        round(

            booksread[

                "HoursSpentReadingPerYear_2024"

            ]

            .mean(),

            1

        )

    )



st.divider()





# ==========================================
# GDP MIXED CHART
# PASTEL SET3 STYLE
# ==========================================


top10_gdp = (

    gdp_data

    .sort_values(

        by="gdp(constant dollars)",

        ascending=False

    )

    .head(10)

)



pastel_colors = [

    "#8DD3C7",

    "#FFFFB3",

    "#BEBADA",

    "#FB8072",

    "#80B1D3",

    "#FDB462",

    "#B3DE69",

    "#FCCDE5",

    "#D9D9D9",

    "#BC80BD"

]



gdp_fig = go.Figure()



# GDP BAR

gdp_fig.add_trace(

    go.Bar(

        x=top10_gdp["country"],


        y=

        top10_gdp[

            "gdp(constant dollars)"

        ] / 1000,


        name="GDP",


        marker=dict(

            color=pastel_colors

        ),


        showlegend=False

    )

)





# BOOK READ LINE

gdp_fig.add_trace(

    go.Scatter(

        x=top10_gdp["country"],


        y=

        top10_gdp[

            "booksreadannually_2024"

        ],


        mode="lines+markers+text",


        name="Books Read",



        line=dict(

            color="#80B1D3",

            width=3

        ),



        marker=dict(

            color="#FB8072",

            size=10,

            line=dict(

                color="white",

                width=1

            )

        ),



        text=

        top10_gdp[

            "booksreadannually_2024"

        ],



        textposition="top center"

    )

)





gdp_fig.update_layout(

    title=dict(

        text=

        "Are Top 10 Highest GDP Countries A Potential Market For Book Publishers To Penetrate?",


        x=0.5,


        xanchor="center",


        font=dict(

            size=18

        )

    ),



    template="simple_white",



    height=650,



    xaxis=dict(

        tickangle=-45,

        title=None

    ),



    yaxis=dict(

        title="GDP (Billion $)"

    ),



    legend=dict(

        orientation="h",

        y=-0.25,

        x=0.5,

        xanchor="center"

    ),



    margin=dict(

        l=50,

        r=50,

        t=80,

        b=120

    )

)




# ==========================================
# TOP 10 BEST-SELLING GENRES PIE CHART
# ==========================================

genre_colors = [

    "#8DD3C7",
    "#FFFFB3",
    "#BEBADA",
    "#FB8072",
    "#80B1D3",
    "#FDB462",
    "#B3DE69",
    "#FCCDE5",
    "#D9D9D9",
    "#BC80BD"

]

genre_fig = go.Figure(

    data=[

        go.Pie(

            labels=genre_data["Genre"],

            values=genre_data["Volume Sales"],

            pull=[0.08] * len(genre_data),

            textinfo="percent",

            marker=dict(

                colors=genre_colors,

                line=dict(
                    color="black",
                    width=1
                )

            ),

            hovertemplate=
            "<b>%{label}</b><br>" +
            "Sales: %{value:,}<br>" +
            "%{percent}<extra></extra>"

        )

    ]

)

genre_fig.update_layout(

    title=dict(

        text="Top 10 Best-Selling Book Genres",

        x=0.5,

        xanchor="center"

    ),

    template="simple_white",

    height=700,

    legend=dict(

        title="Genres",

        orientation="v",

        x=1.02,

        y=0.5,

        xanchor="left",

        yanchor="middle"

    ),

    margin=dict(

        l=50,

        r=220,

        t=80,

        b=50

    )

)



# ==========================================
# CREATE TABS
# ==========================================


tab1, tab2 = st.tabs(

    [

        "Data Visualization",

        "Dataset"

    ]

)

# ==========================================
# TAB 1
# MAP + TOP 10 + GDP CHART
# ==========================================


with tab1:


    # ======================================
    # FIRST ROW
    # MAP + BAR CHART SIDE BY SIDE
    # ======================================

    map_col, chart_col = st.columns(

        [1.6, 1]

    )



    # ======================================
    # WORLD MAP
    # ======================================

    with map_col:


        fig = go.Figure()



        fig.add_trace(

            go.Choropleth(

                locations=

                booksread["iso_alpha"],


                z=

                booksread[selected_metric],


                text=

                booksread["country"],


                colorscale=

                selected_color,


                marker_line_color="black",


                marker_line_width=0.4,



                colorbar=dict(

                    title="",


                    x=-0.08,


                    y=0.5,


                    xanchor="right",


                    yanchor="middle",


                    len=0.5,


                    thickness=14,


                    tickformat=".0f"

                ),



                hovertemplate=

                "<b>%{text}</b><br>" +

                selected_metric_label +

                ": %{z}<extra></extra>"

            )

        )





        fig.update_layout(

            title=dict(

                text=

                f" 🌍{selected_metric_label} by Country",


                x=0.5,


                xanchor="center",


                y=0.98,


                yanchor="top",


                font=dict(

                    size=20

                )

            ),



            height=850,



            margin=dict(

                l=20,

                r=20,

                t=70,

                b=20

            )

        )





        fig.update_geos(

            fitbounds="locations",


            projection_type="natural earth",


            showcountries=True,


            countrycolor="black",


            showocean=True,


            oceancolor="lightblue",


            showland=True,


            landcolor="lightgrey",


            showcoastlines=True

        )





        st.plotly_chart(

            fig,

            use_container_width=True

        )







    # ======================================
    # TOP 10 BAR CHART
    # COLOR SCALE ON
    # LEGEND OFF
    # ======================================

    with chart_col:


        st.subheader(

            "Top 10 Countries"

        )



        top10 = (

            booksread

            .sort_values(

                by=selected_metric,

                ascending=False

            )

            .head(10)

        )





        bar_fig = px.bar(

            top10,


            x=selected_metric,


            y="country",


            orientation="h",


            color=selected_metric,


            color_continuous_scale=

            selected_color,


            text=selected_metric

        )





        bar_fig.update_traces(

            textposition="outside",


            cliponaxis=False

        )





        bar_fig.update_layout(

            height=650,


            margin=dict(

                l=10,

                r=90,

                t=20,

                b=20

            ),


            # REMOVE LEGEND BOX

            showlegend=False,


             # REMOVE COLOR SCALE
    coloraxis_showscale=False,


    # REMOVE X AND Y AXIS TITLES
    xaxis=dict(

        title=None,

        showticklabels=False

    ),


    yaxis=dict(

        title=None, 
        categoryorder="total ascending"

    )

)
        





        st.plotly_chart(

            bar_fig,

            use_container_width=True

        )







    # ======================================
    # SECOND ROW
    # GDP MIXED CHART UNDER MAP + BAR
    # ======================================


    st.divider()



    st.subheader(

        "📈 Market Entry Evaluation Based On Economic and Cultural Indicators "

    )



    st.plotly_chart(

        gdp_fig,

        use_container_width=True

    )


st.divider()

st.subheader(
    "📚 The Evaluation of Book Product Lines"
)

st.plotly_chart(
    genre_fig,
    use_container_width=True
)





# ==========================================
# TAB 2
# DATASET
# ==========================================


with tab2:


    st.subheader(

        "Dataset"

    )

    st.divider()



    st.subheader(
        "Reading Habits Dataset"
    )


    st.dataframe(

        booksread,

        use_container_width=True

    )


    st.write(

        f"Rows: {booksread.shape[0]} | "
        f"Columns: {booksread.shape[1]}"

    )



    st.divider()



    st.subheader(
        "GDP Dataset"
    )


    st.dataframe(

        gdp_data,

        use_container_width=True

    )


    st.write(

        f"Rows: {gdp_data.shape[0]} | "
        f"Columns: {gdp_data.shape[1]}"

    )



    st.divider()



    st.subheader(
        "Best-Selling Book Genres Dataset"
    )


    st.dataframe(

        genre_data,

        use_container_width=True

    )


    st.write(

        f"Rows: {genre_data.shape[0]} | "
        f"Columns: {genre_data.shape[1]}"

    )
    