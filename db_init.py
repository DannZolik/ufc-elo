import mysql.connector
import json

# Function to calculate new ELO ratings
def calculate_elo(winner_elo, loser_elo, method):
    k = 40

    if 'SUB' in method or 'KO/TKO' in method:
        k *= 1.20

    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_elo - loser_elo) / 400))
    
    new_winner_elo = round(winner_elo + k * (1 - expected_winner), 2)
    new_loser_elo = round(loser_elo + k * (0 - expected_loser), 2)
    
    return new_winner_elo, new_loser_elo

# Connect to MySQL using root without password
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

# Create a cursor object to execute SQL queries
cursor = connection.cursor()

# Check if the database 'ufc_stats' exists
cursor.execute("SHOW DATABASES LIKE 'ufc_stats'")
database_exists = cursor.fetchone()

# Drop the database if it exists
if database_exists:
    print("Database 'ufc_stats' exists. Dropping it...")
    cursor.execute("DROP DATABASE ufc_stats")

# Create the database
print("Creating database 'ufc_stats'...")
cursor.execute("CREATE DATABASE ufc_stats")

# Select the newly created database
cursor.execute("USE ufc_stats")

# Create the 'fighters' table
print("Creating table 'fighters'...")
cursor.execute("""
    CREATE TABLE fighters (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        elo FLOAT(10, 2) DEFAULT 1000,
        max_elo FLOAT(10, 2) DEFAULT 1000
    )
""")

# Create the 'fights' table
print("Creating table 'fights'...")
cursor.execute("""
    CREATE TABLE fights (
        id INT AUTO_INCREMENT PRIMARY KEY,
        winner_id INT NOT NULL,
        loser_id INT NOT NULL,
        winner_before_elo FLOAT(10, 2),
        winner_after_elo FLOAT(10, 2),
        loser_before_elo FLOAT(10, 2),
        loser_after_elo FLOAT(10, 2),
        method VARCHAR(255), 
        FOREIGN KEY (winner_id) REFERENCES fighters(id),
        FOREIGN KEY (loser_id) REFERENCES fighters(id)
    )
""")

# Create trigger to update max_elo
print("Creating trigger to update max_elo...")
cursor.execute("""
    CREATE TRIGGER update_max_elo 
    BEFORE UPDATE ON fighters 
    FOR EACH ROW 
    BEGIN 
        IF NEW.elo > NEW.max_elo THEN 
            SET NEW.max_elo = NEW.elo; 
        END IF; 
    END;
""")

# Load fight data from the JSON file
with open('fight_results.json', 'r') as file:
    fight_data = json.load(file)


# Extract unique fighter names from the fight data
unique_fighters = set()
for fight in fight_data:
    unique_fighters.add(fight['winner'])
    unique_fighters.add(fight['loser'])

# Insert unique fighters into the 'fighters' table
print("Inserting unique fighters into the 'fighters' table...")
for fighter in unique_fighters:
    cursor.execute("INSERT INTO fighters (name) VALUES (%s)", (fighter,))

# Commit the changes to the database
connection.commit()

# Insert fight records into the 'fights' table and update ELO ratings
print("Inserting fight records into the 'fights' table and updating ELO ratings...")
for fight in fight_data:
    # Get the winner's ID and elo
    cursor.execute("SELECT id, elo FROM fighters WHERE name = %s", (fight['winner'],))
    winner_id, winner_elo = cursor.fetchone()
    
    # Get the loser's ID and elo
    cursor.execute("SELECT id, elo FROM fighters WHERE name = %s", (fight['loser'],))
    loser_id, loser_elo = cursor.fetchone()

    # Calculate the new ELO ratings for the winner and loser
    new_winner_elo, new_loser_elo = calculate_elo(winner_elo, loser_elo, fight['method'])
    
    # Insert the fight record into the 'fights' table
    cursor.execute("INSERT INTO fights (winner_id, loser_id, winner_before_elo, winner_after_elo, loser_before_elo, loser_after_elo, method) VALUES (%s, %s, %s, %s, %s, %s, %s)", (
        winner_id, loser_id, winner_elo, new_winner_elo, loser_elo, new_loser_elo, fight['method']
    ))
    
    
    
    # Update the ELO ratings of the winner and loser in the 'fighters' table
    cursor.execute("UPDATE fighters SET elo = %s, max_elo = GREATEST(max_elo, %s) WHERE id = %s", (new_winner_elo, new_winner_elo, winner_id))
    cursor.execute("UPDATE fighters SET elo = %s WHERE id = %s", (new_loser_elo, loser_id))

# Commit the changes to the database
connection.commit()

# Close the cursor and the connection
cursor.close()
connection.close()

print("Database and tables created successfully.")
