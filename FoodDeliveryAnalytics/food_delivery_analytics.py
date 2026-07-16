import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

# Global Variables

cleaned_df = None
category_summary = None
join_result = None


def load_sample_data():
    data = {
        "order_id": [101,102,103,104,105,106,107,108,109,110,110],
        "restaurant_id":[1,2,3,1,2,3,1,2,3,1,1],
        "category":["Pizza","Burger","Biryani","Pizza",None,"Biryani","Pizza","Burger","Biryani","Pizza","Pizza"],
        "city":["Ahmedabad","Surat","Vadodara","Ahmedabad","Surat","Vadodara","Ahmedabad","Surat","Vadodara","Ahmedabad","Ahmedabad"],
        "order_value":[250,300,np.nan,280,5000,350,260,310,340,290,290],
        "delivery_time":[30,np.nan,45,35,50,40,32,38,np.nan,36,36],
        "rating":[4.5,4.2,np.nan,4.8,4.0,4.3,4.6,4.1,4.4,np.nan,np.nan]
    }

    return pd.DataFrame(data)

# Option 1

def load_clean_data():

    global cleaned_df

    df = load_sample_data()

    print("\n========== BEFORE CLEANING ==========")
    print(df)
    print("\nMissing Values")
    print(df.isnull().sum())

    print("\nDuplicates:", df.duplicated().sum())

    # Missing Value Handling
    df["order_value"].fillna(df["order_value"].median(), inplace=True)
    df["delivery_time"].fillna(df["delivery_time"].median(), inplace=True)
    df["rating"].fillna(df["rating"].mean(), inplace=True)
    df["category"].fillna(df["category"].mode()[0], inplace=True)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Outlier Detection using IQR
    Q1 = df["order_value"].quantile(0.25)
    Q3 = df["order_value"].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    df["order_value"] = df["order_value"].clip(lower=lower, upper=upper)

    cleaned_df = df

    print("\n========== AFTER CLEANING ==========")
    print(cleaned_df)

    print("\nMissing Values")
    print(cleaned_df.isnull().sum())

    print("\nDuplicates:", cleaned_df.duplicated().sum())

# Option 2

def sql_analysis():

    global cleaned_df
    global category_summary
    global join_result

    if cleaned_df is None:
        print("\nPlease load data first.")
        return

    conn = sqlite3.connect("food_delivery.db")

    restaurants = pd.DataFrame({
        "restaurant_id":[1,2,3],
        "restaurant_name":["Dominos","McDonalds","Behrouz"],
        "category":["Pizza","Burger","Biryani"],
        "city":["Ahmedabad","Surat","Vadodara"]
    })

    restaurants.to_sql("restaurants", conn,
                       if_exists="replace",
                       index=False)

    cleaned_df.to_sql("orders",
                      conn,
                      if_exists="replace",
                      index=False)

    # GROUP BY Query
    query1 = """
    SELECT category,
           COUNT(*) AS Total_Orders,
           SUM(order_value) AS Revenue,
           AVG(delivery_time) AS Avg_Delivery
    FROM orders
    GROUP BY category
    """

    category_summary = pd.read_sql(query1, conn)

    print("\nCATEGORY SUMMARY")
    print(tabulate(category_summary,
                   headers="keys",
                   tablefmt="grid",
                   showindex=False))

    # JOIN Query
    query2 = """
    SELECT
    r.restaurant_name,
    r.city,
    o.order_id,
    o.order_value,
    o.delivery_time
    FROM restaurants r
    JOIN orders o
    ON r.restaurant_id=o.restaurant_id
    """

    join_result = pd.read_sql(query2, conn)

    print("\nJOIN RESULT")
    print(tabulate(join_result,
                   headers="keys",
                   tablefmt="grid",
                   showindex=False))

    conn.close()

# Option 3

def view_charts():

    global cleaned_df

    if cleaned_df is None:
        print("\nPlease load data first.")
        return

    fig, ax = plt.subplots(1,2,figsize=(14,5))

    # Count Plot
    sns.countplot(data=cleaned_df,
                  x="category",
                  ax=ax[0])

    ax[0].set_title("Orders by Category")
    ax[0].set_xlabel("Category")
    ax[0].set_ylabel("Orders")

    # Add count values
    for container in ax[0].containers:
        ax[0].bar_label(container, fmt="%d", padding=3)

    # Bar Plot
    sns.barplot(data=cleaned_df,
                x="city",
                y="delivery_time",
                ax=ax[1])

    ax[1].set_title("Average Delivery Time by City")
    ax[1].set_xlabel("City")
    ax[1].set_ylabel("Average Delivery Time")

    # Add values above the error bars
    for line in ax[1].lines:
        x = line.get_xdata()[0]
        y = max(line.get_ydata())
        ax[1].text(x, y + 0.5,
                   f"{y:.2f}",
                   ha="center",
                   va="bottom",
                   fontsize=10,
                   fontweight="bold")

    plt.tight_layout()
    plt.show()

# Option 4

def export_report():

    global cleaned_df
    global category_summary
    global join_result

    if cleaned_df is None:
        print("\nNothing to export.")
        return

    with pd.ExcelWriter("food_delivery_report.xlsx") as writer:

        cleaned_df.to_excel(writer,
                            sheet_name="Cleaned Data",
                            index=False)

        if category_summary is not None:
            category_summary.to_excel(writer,
                                      sheet_name="Category Summary",
                                      index=False)

        if join_result is not None:
            join_result.to_excel(writer,
                                 sheet_name="Join Result",
                                 index=False)

    import os

    print("\nReport exported successfully.")
    print("Location:", os.path.abspath("food_delivery_report.xlsx"))


# -----------------------------
# Main Menu
# -----------------------------
while True:

    print("\n")
    print("="*45)
    print(" FOOD DELIVERY ANALYTICS SYSTEM ")
    print("="*45)
    print("1. Load & Clean Data")
    print("2. Run SQL Analysis")
    print("3. View Charts")
    print("4. Export Report")
    print("0. Exit")

    choice = input("\nEnter Choice: ")

    if choice == "1":
        load_clean_data()

    elif choice == "2":
        sql_analysis()

    elif choice == "3":
        view_charts()

    elif choice == "4":
        export_report()

    elif choice == "0":
        print("\nThank You!")
        break

    else:
        print("\nInvalid Choice")