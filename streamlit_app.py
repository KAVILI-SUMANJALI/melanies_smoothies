# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
streamlit.title('My Parents New Healthy Diner')
# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie"""
)



name_on_order= st.text_input("Name On Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

cnx=st.connection("snowflake")
# Get the Snowflake session
session = cnx.session()

# Get only the FRUIT_NAME column
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME")
)

# Keep this commented out as instructed by the lab
# st.dataframe(data=my_dataframe, use_container_width=True)

# Convert FRUIT_NAME values into a Python list
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Multiselect widget
ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list
)

if ingredients:
    ingredients_string = ""

    for fruit_chosen in ingredients:
        ingredients_string += fruit_chosen

    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    st.write(my_insert_stmt)

    submit = st.button("Submit Order")
    

    if submit:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
        import requests  
smoothiefroot_response = requests.get("[https://my.smoothiefroot.com/api/fruit/watermelon](https://my.smoothiefroot.com/api/fruit/watermelon)")  
#st.text(smoothiefroot_response.json())
st_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
