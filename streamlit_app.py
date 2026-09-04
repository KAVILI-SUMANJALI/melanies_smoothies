import requests

for fruit_chosen in ingredients:

    if fruit_chosen == "Jackfruit":
        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/Jack%20Fruit"
        )
    else:
        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
        )

    st.write(response.status_code)
    st.write(response.json())
