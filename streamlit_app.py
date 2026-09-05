# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Titles
st.title('My Parents New Healthy Diner')
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom smoothie"""
)

# Name on order
name_on_order = st.text_input("Name On Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit names and API search values
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert to Pandas
pd_df = my_dataframe.to_pandas()

# Fruit list
fruit_list = pd_df["FRUIT_NAME"].tolist()

# Multiselect
ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients:

    ingredients_string = ''

    for fruit_chosen in ingredients:

        # IMPORTANT FOR DORA:
        # fruit + SPACE, not comma
        ingredients_string += fruit_chosen + ' '

        # Get SEARCH_ON value
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        st.write(
            'The search value for ',
            fruit_chosen,
            ' is ',
            search_on,
            '.'
        )

        # Call SmoothieFroot API
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        # Display nutrition data
        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    st.write(ingredients_string)

    # Insert order
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order)
        VALUES ('""" + ingredients_string + """','""" + name_on_order + """')
    """

    st.write(my_insert_stmt)

    submit = st.button("Submit Order")

    if submit:
        session.sql(my_insert_stmt).collect()

        st.success(
            'Your Smoothie is ordered!',
            icon="✅"
        )
