This repo contains the code for a discord bot that uses python and sql to keep track of and update a leaderboard for a game show.
To create the sql database and table use these commands:{

import mysql.connector

mydb = mysql.connector.connect(
    host = [localhost or other],
    user = [username],
    password = [password],
    database= [name]
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE LeaderboardTestTable")
mycursor.execute("CREATE TABLE TestTable1 (discordId VARCHAR(30) PRIMARY KEY, discord_name VARCHAR(50), weekly_score tinyint UNSIGNED, all_time_score smallint UNSIGNED, strikes tinyint UNSIGNED)")
mydb.commit()

}

This will generate the sql database and table that can be interacted with with the files writen in this repo. Make sure to update all the "mydb"s in the code to the correct parameters before use.
