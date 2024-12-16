import mysql.connector
from prettytable import PrettyTable

def get_expected_elo(winner_elo, loser_elo):
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_elo - loser_elo) / 400))
    return expected_winner, expected_loser

# Connect to the MySQL database
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

fighter1 = "Josefine Knutsson"
fighter2 = "Piera Rodriguez"

# Create a cursor object to execute SQL queries
cursor = connection.cursor()

# Use the UFC stats database
cursor.execute("USE ufc_stats")

# Retrieve fighter 1 information
cursor.execute("SELECT id, elo FROM fighters WHERE name = %s", ([fighter1]))
fighter1_id, fighter1_elo = cursor.fetchone()

# Retrieve fighter 2 information
cursor.execute("SELECT id, elo FROM fighters WHERE name = %s", ([fighter2]))
fighter2_id, fighter2_elo = cursor.fetchone()

# Calculate expected ELO scores for both fighters
fighter1_expectation, fighter2_expectation = get_expected_elo(fighter1_elo, fighter2_elo)

# Create a table to display the results
table = PrettyTable()
table.field_names = ["Fighter", "ELO", "Win Chance (%)"]
table.add_row([fighter1, fighter1_elo, round(fighter1_expectation * 100, 2)])
table.add_row([fighter2, fighter2_elo, round(fighter2_expectation * 100, 2)])

# Print the table
print(table)

# Close the cursor and the connection
cursor.close()
connection.close()
