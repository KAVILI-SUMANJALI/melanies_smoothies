# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

st.title('My Parents New Healthy Diner')

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom smoothie"""
)

name_on_order = st.text_input("Name On Smoothie:")

st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")

# Get the Snowflake session
session = cnx.session()

# Get FRUIT_NAME and SEARCH_ON columns
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert Snowflake dataframe to pandas dataframe
pd_df = my_dataframe.to_pandas()

# Convert FRUIT_NAME values into a Python list
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Multiselect widget
ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list
)

if ingredients:
    ingredients_string = ''

    for fruit_chosen in ingredients:

        ingredients_string += fruit_chosen + ','

        # Find the SEARCH_ON value for the selected fruit
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        # Display the search value
        st.write(
            'The search value for ',
            fruit_chosen,
            ' is ',
            search_on,
            '.'
        )

        # Call SmoothieFroot API using SEARCH_ON
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        # Display the API response
        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    st.write(ingredients_string)

    # Create INSERT statement
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    st.write(my_insert_stmt)

    # Submit button
    submit = st.button("Submit Order")

    if submit:
        session.sql(my_insert_stmt).collect()

        st.success(
            'Your Smoothie is ordered!',
            icon="✅"
        )
