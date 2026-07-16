import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

db_file = "food_delivery.db"

# Check if database exists
if not os.path.exists(db_file):
    print("Database not found. Creating a new database...")

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        order_id INTEGER PRIMARY KEY,
        restaurant_name TEXT,
        category TEXT,
        order_value REAL,
        rating REAL,
        delivery_time_mins REAL
    )
    """)

    # Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]

    # Insert sample data only if table is empty
    if count == 0:
        data = [
            (1,"Pizza Hub","Pizza",450,4.8,30),
            (2,"Pizza Hub","Pizza",380,4.7,28),
            (3,"Pizza Hub","Pizza",520,4.9,25),
            (4,"Pizza Hub","Pizza",410,4.6,27),
            (5,"Pizza Hub","Pizza",470,4.8,26),

            (6,"Burger Point","Burger",300,4.5,20),
            (7,"Burger Point","Burger",350,4.6,22),
            (8,"Burger Point","Burger",320,4.7,24),
            (9,"Burger Point","Burger",310,4.5,23),
            (10,"Burger Point","Burger",340,4.8,21),

            (11,"Spice Villa","Indian",550,4.9,35),
            (12,"Spice Villa","Indian",600,4.8,32),
            (13,"Spice Villa","Indian",580,4.7,34),
            (14,"Spice Villa","Indian",620,4.9,31),
            (15,"Spice Villa","Indian",590,4.8,33),

            (16,"Food Corner","Chinese",250,4.2,40),
            (17,"Food Corner","Chinese",270,4.1,38),
            (18,"Food Corner","Chinese",260,4.3,39)
        ]

        cursor.executemany(
            "INSERT INTO orders VALUES (?,?,?,?,?,?)",
            data
        )

        conn.commit()

    # SQL Query
    query = """
    SELECT
        restaurant_name,
        AVG(rating) AS avg_rating,
        COUNT(order_id) AS total_orders,
        SUM(order_value) AS total_revenue
    FROM orders
    GROUP BY restaurant_name
    HAVING COUNT(order_id) >= 5
    ORDER BY avg_rating DESC
    LIMIT 3;
    """

    df = pd.read_sql(query, conn)

    if df.empty:
        print("No restaurant has at least 5 orders.")
    else:
        total_revenue = df["total_revenue"].sum()

        df["revenue_share"] = (
            df["total_revenue"] / total_revenue
        ) * 100

        print("\nTop 3 Restaurants")
        print(df)

        plt.figure(figsize=(8,5))

        bars = plt.barh(
            df["restaurant_name"],
            df["avg_rating"]
        )

        for bar, share in zip(bars, df["revenue_share"]):
            plt.text(
                bar.get_width()+0.02,
                bar.get_y()+bar.get_height()/2,
                f"{share:.1f}%",
                va="center"
            )

        plt.xlabel("Average Rating")
        plt.ylabel("Restaurant")
        plt.title("Top 3 Restaurants by Average Rating")
        plt.xlim(0,5)

        plt.show()

    conn.close()

except sqlite3.Error as e:
    print("Database Error:", e)

except Exception as e:
    print("Unexpected Error:", e)