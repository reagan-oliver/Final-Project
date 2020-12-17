"""
Name:       Reagan Oliver
CS230:      Section 05
Data:       Cambridge Airbnb Data
Summary:
There are two main functions of this program:
1.) Have property owners input info about their property and help determine a possible price for it
    - produces an actual number based on inputs from the sidebar
    - prints three charts that compare the price of their property to others based on their inputs

2.) Have potential renters add specifications about their property to help determine where to stay
    - produces a list of the properties with the specific features they enter
    - prints a map with the location of the different properties that fit their inputs
"""

import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import pydeck as pdk

# Menus and dataframes
R_MENU = ["pr - Private Room\n", "sr - Shared Room\n", "eh - Entire Home/Apartment"]

N_MENU = ["wc - West Cambridge\n", "nc - North Cambridge\n",  "tp - The Port\n", "nn - Neighborhood Nine\n",
          "rs - Riverside\n", "cp - Cambridgeport\n", "ag - Agassiz\n", "mc - Mid-Cambridge\n",
          "ec - East Cambridge\n", "wh - Wellington-Harrington\n", "sh - Strawberry Hill\n", "am - Area 2/MIT\n",
          "ch - Cambridge Highlands\n"]

ROOM_CODES = {"eh": ["R_Type1", "Entire home/apt"],
              "pr": ["R_Type2", "Private room"],
              "sr": ["R_Type3", "Shared room"]}

NEIGH_CODES = {"wc": ["N1", "West Cambridge"], "nc": ["N2", "North Cambridge"],
               "tp": ["N3", "The Port"], "nn": ["N4", "Neighborhood Nine"],
               "rs": ["N5", "Riverside"], "cp": ["N6", "Cambridgeport"],
               "ag": ["N7", "Agassiz"], "mc": ["N8", "Mid-Cambridge"],
               "ec": ["N9", "East Cambridge"], "wh": ["N10", "Wellington-Harrington"],
               "sh": ["N11", "Strawberry Hill"], "am": ["N12", "Area 2/MIT"],
               "ch": ["N13", "Cambridge Highlands"]}


def read_data():
    # Reads in the data
    df = pd.read_csv("airbnb_cambridge_listings_20201123.csv", usecols=[5, 6, 7, 8, 9, 10])
    n_list = []
    t_list = []
    for n in df["neighbourhood"]:
        if n not in n_list:
            n_list.append(n)

    for t in df["room_type"]:
        if t not in t_list:
            t_list.append(t)

    count = 0
    for r in t_list:
        new_col = []
        for i in df["room_type"]:
            if r == i:
                new_col.append(1)
            else:
                new_col.append(0)
        count += 1
        new_title = f"R_Type{str(count)}"
        df[new_title] = new_col

    count = 0
    for n in n_list:
        new_col = []
        for i in df["neighbourhood"]:
            if n == i:
                new_col.append(1)
            else:
                new_col.append(0)
        count += 1
        new_title = f"N{str(count)}"
        df[new_title] = new_col

    new_df = df.drop([556])
    return new_df


def regression(data, list, NH, RT, MN):
    # Runs a regression based on the data and produces a recommended price
    x = data[list]
    y = data["price"]

    model = linear_model.LinearRegression()
    model.fit(x, y)

    pred_list = [int(MN)]

    for r in list[1:4]:
        if r == ROOM_CODES[RT][0]:
            pred_list.append(1)
        else:
            pred_list.append(0)

    for n in list[4:17]:
        if n == NEIGH_CODES[NH]:
            pred_list.append(1)
        else:
            pred_list.append(0)

    price = model.predict([pred_list])
    price_num = price[0]
    return price_num


def scatter_charts(data, v, price):
    # Creates scatter plots based on each variable

    if v in ROOM_CODES.keys():
        plt.figure(0)
        n = plt.scatter(data["room_type"], data["price"], c="royalblue")
        m = plt.scatter(ROOM_CODES[v][1], price, c="firebrick")
        plt.legend((n, m), ("Data", "Your Property"), loc='best')
        plt.title("Price by Room Type")
        plt.xlabel("Room Type")
        plt.ylabel("Price per Night")
        st.pyplot(plt)

    elif v in NEIGH_CODES.keys():
        code_list = []
        for k in NEIGH_CODES.keys():
            code_list.append(k)
        x = np.arange(len(code_list))

        plt.figure(1)
        n = plt.scatter(data["neighbourhood"], data["price"], c="royalblue")
        m = plt.scatter(NEIGH_CODES[v][1], price, c="firebrick")
        plt.xticks(x, code_list)
        plt.legend((n, m), ("Data", "Your Property"), loc='best')
        plt.title("Price by Neighborhood")
        plt.xlabel("Neighborhood")
        plt.ylabel("Price per Night")
        st.pyplot(plt)

    else:
        plt.figure(2)
        n = plt.scatter(data["minimum_nights"], data["price"], c="royalblue")
        m = plt.scatter(v, price, c="firebrick")
        plt.legend((n, m), ("Data", "Your Property"), loc='best')
        plt.title("Price by Minimum Nights")
        plt.xlabel("Minimum Nights")
        plt.ylabel("Price per Night")
        st.pyplot(plt)


def main():
    data = read_data()

    # Sidebar option selection
    st.sidebar.header("Navigation:")
    choice = st.sidebar.radio("Pick one of the following: ", ("Owners", "Renters"))

    if choice == "Owners":

        st.title("Owners: Determine a Price for Your Property")
        st.write("Please use the options to the left to modify the outputs displayed below.")

        # Print menus
        st.header("Room Codes:")
        cols = st.beta_columns(3)
        cols[0].write(f"{R_MENU[0]}")
        cols[1].write(f"{R_MENU[1]}")
        cols[2].write(f"{R_MENU[2]}")

        st.header("Neighborhood Codes:")
        out1 = ("\n".join(map(str, N_MENU[0:5])))
        out2 = ("\n".join(map(str, N_MENU[5:10])))
        out3 = ("\n".join(map(str, N_MENU[10:13])))

        cols = st.beta_columns(3)
        cols[0].write(f"{out1}")
        cols[1].write(f"{out2}")
        cols[2].write(f"{out3}")

        # Create Sidebar
        st.sidebar.header("Owner Inputs")
        rt = st.sidebar.text_input("Enter one of the room type codes: ", "pr").lower()
        nh = st.sidebar.text_input("Enter one of the neighborhood codes: ", "wc").lower()
        ni = st.sidebar.slider("Enter the minimum nights you require at your property: ", 1, 250)

        # If statements check for errors
        if rt in ROOM_CODES.keys():
            if nh in NEIGH_CODES.keys():
                # Run and print regression output
                col_list = []
                for col in data[data.columns]:
                    col_list.append(col)
                del col_list[0:5]
                price = regression(data, col_list, nh, rt, ni)
                st.header('Pricing:')
                st.write(f"According to your inputs, you should list \
                property for about ${price:.2f} a night on Airbnb!")

                # Print scatter plot for each variable
                st.header("Charts:")
                scatter_charts(data, nh, price)
                scatter_charts(data, rt, price)
                scatter_charts(data, ni, price)
            else:
                st.write("Invalid neighborhood type please try again.")
        else:
            st.write("Invalid room type please try again.")


    elif choice == "Renters":
        st.title("Renters: Find Your Ideal Property")
        st.write("Please use the options to the left to modify the outputs displayed below.")

        # Create lists of names
        r_list = []
        for k in ROOM_CODES:
            r_list.append(ROOM_CODES[k][1])
        n_list = []
        for k in NEIGH_CODES:
            n_list.append(NEIGH_CODES[k][1])

        # Create Sidebar
        st.sidebar.header("Buyer Inputs")
        nights = st.sidebar.slider("Number of Nights:", 1, 250)
        price = st.sidebar.slider("Maximum Price per Night:", 1, 950)
        room = st.sidebar.radio("Room Type:", r_list)
        nhood = st.sidebar.radio("Neighborhood:", n_list)
        sort = st.sidebar.radio("Sort by:", ["Price: Low to High", "Price: High to Low",
                                             "Nights: Low to High", "Nights: High to Low"])

        # Use sidebar inputs to modify the dataframe
        for i in data["room_type"].index:
            if data["room_type"][i] != room:
                data = data.drop(i, axis=0)

        for i in data["neighbourhood"].index:
            if data["neighbourhood"][i] != nhood:
                data = data.drop(i, axis=0)

        for i in data["price"].index:
            if data["price"][i] > price:
                data = data.drop(i, axis=0)

        for i in data["minimum_nights"].index:
            if data["minimum_nights"][i] > nights:
                data = data.drop(i, axis=0)

        cols = ["neighbourhood", "room_type", "minimum_nights", "price", "latitude", "longitude"]
        del_cols = []
        for d in data:
            if d not in cols:
                del_cols.append(d)

        data = data.drop(columns=del_cols)

        new_data = data.drop(columns=["latitude", "longitude"])
        new_data = new_data.rename(columns={"neighbourhood": "Neighborhood",
                                            "room_type": "Room Type",
                                            "price": "Price per Night",
                                            "minimum_nights": "Minimum Nights"})

        # Sort Data
        if sort == "Price: Low to High":
            new_data = new_data.sort_values(by="Price per Night", ascending=True)
        elif sort == "Price: High to Low":
            new_data = new_data.sort_values(by="Price per Night", ascending=False)
        elif sort == "Nights: Low to High":
            new_data = new_data.sort_values(by="Minimum Nights", ascending=True)
        elif sort == "Nights: High to Low":
            new_data = new_data.sort_values(by="Minimum Nights", ascending=False)

        # Add index column for tool tip lable
        index_list = []
        for i in data.index:
            index_list.append(i)
        data["Index"] = index_list

        # Print Dataframe
        st.header("Your Listings")
        st.dataframe(new_data)

        # Check Dataframe to make sure it has data
        if data.empty:
            st.write("No properties match your search!")
        else:
            # Print Map
            st.header("Listing Map")

            MAPKEY = "pk.eyJ1IjoiY2hlY2ttYXJrIiwiYSI6ImNrOTI0NzU3YTA0azYzZ21rZHRtM2tuYTcifQ.6aQ9nlBpGbomhySWPF98DApk.eyJ1IjoiY2hlY2ttYXJrIiwiYSI6ImNrOTI0NzU3YTA0azYzZ21rZHRtM2tuYTcifQ.6aQ9nlBpGbomhySWPF98DA"

            view_state = pdk.ViewState(
                latitude=data["latitude"].mean(),
                longitude=data["longitude"].mean(),
                zoom=11,
                pitch=0)

            layer1 = pdk.Layer('ScatterplotLayer',
                      data=data,
                      get_position='[longitude, latitude]',
                      get_radius=100,
                      get_color=[0,0,255],
                      pickable=True
                      )

            tool_tip = {"html": "Property Number:<br/> <b>{Index}</b> ",
                "style": { "backgroundColor": "steelblue",
                            "color": "white"}
              }

            output = pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=view_state,
                mapbox_key=MAPKEY,
                layers=[layer1],
                tooltip=tool_tip
            )

            st.pydeck_chart(output)
main()

