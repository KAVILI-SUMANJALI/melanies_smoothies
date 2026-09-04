# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Title
st.title('My Parents New Healthy Diner')

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom smoothie"""
)

# Name on order
name_on_order = st.text_input("Name On Smoothie:")

st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")

# Get the Snowflake session
session = cnx.session()

# Get FRUIT_NAME and SEARCH_ON columns
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert Snowpark dataframe to Pandas dataframe
pd_df = my_dataframe.to_pandas()

# Create list of fruit names for the multiselect
fruit_list = pd_df["FRUIT_NAME"].tolist()

# Multiselect widget
ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Process selected ingredients
if ingredients:

    ingredients_string = ''

    for fruit_chosen in ingredients:

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

        # Call the SmoothieFroot API using SEARCH_ON
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        # Display the API data
        st_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

        # Add fruit to ingredients string
        ingredients_string += fruit_chosen + ','

    # Remove the final comma
    ingredients_string = ingredients_string.rstrip(',')

    # Display ingredients
    st.write(ingredients_string)

    # Create INSERT statement
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order)
        VALUES ('""" + ingredients_string + """','""" + name_on_order + """')
    """

    # Display INSERT statement
    st.write(my_insert_stmt)

    # Submit button
    submit = st.button("Submit Order")

    if submit:

        session.sql(my_insert_stmt).collect()

        st.success(
            'Your Smoothie is ordered!',
            icon="✅"
        )
