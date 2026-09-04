# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Title
st.title('My Parents New Healthy Diner')

st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom smoothie"""
)

# Name on order
name_on_order = st.text_input("Name On Smoothie:")

st.write(
    "The name on your smoothie will be:",
    name_on_order
)

# Connect to Snowflake
cnx = st.connection("snowflake")

# Get the Snowflake session
session = cnx.session()

# Get FRUIT_NAME and SEARCH_ON
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert to pandas dataframe
pd_df = my_dataframe.to_pandas()

# Create fruit list for multiselect
fruit_list = pd_df["FRUIT_NAME"].tolist()

# Multiselect
ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list
)

if ingredients:

    ingredients_string = ''

    for fruit_chosen in ingredients:

        # Add comma only between fruits
        if ingredients_string:
            ingredients_string += ','

        # Keep the GUI name for the order
        ingredients_string += fruit_chosen

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

        # Call SmoothieFroot API using SEARCH_ON
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/"
            + search_on
        )

        # Display nutrition information
        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Display ingredients
    st.write(ingredients_string)

    # Insert order into Snowflake
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order)
        VALUES ('""" + ingredients_string + """','""" + name_on_order + """')
    """

    st.write(my_insert_stmt)

    # Submit order
    submit = st.button("Submit Order")

    if submit:

        session.sql(my_insert_stmt).collect()

        st.success(
            'Your Smoothie is ordered!',
            icon="✅"
        )
