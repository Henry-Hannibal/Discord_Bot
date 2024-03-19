import os
import mysql.connector
from tabulate import tabulate



discordUserCommandsList = """OUT: ```COMMANDS LIST:
  - ADD POINT: \"!l w @name\" This will add a point to the player with the given discord id.
  - ADD STRIKE: \"!l l @name\" This will add a strike to the player with the given discord id (After three strikes, the player is out and strikes for specified player is reset).
  - SUBTRACT POINT: \"!l -w @name\" This will subtract a point from the player with the given discord id.
  - SUBTRACT STRIKE: \"!l -l @name\" This will subtract a strike from the player with the given discord id (Mininmum strikes is 0).
  
  - GET PLAYER DATA: \"!l q @name\" This will output all data with the associated player discord id.
  - LIST WEEKLY TOP PLAYERS: \"!l top [insert integer]\" This will output the weekly score top players, the number of top players is determined by the user input.
  - LIST ALL TIME TOP PLAYERS: \"!l all_time_top [OPTIONAL: insert integer]\" This will output the all time top scoring players, the number of top players is determined by the user input.
  - SET UP FOR NEW WEEK: \"!l new_week!\" This will add all weekly scores to the all time scores, reset all strikes to 0, and set all players display to 0.
  
  - ADD NEW PLAYER: \"!l add @name [Player name, max 50 characters]\" This will add a new player to the leaderboard with the name given .
  - DELETE PLAYER: \"!l delete_player @name\" This will delete all data of the player with the given discord id.
  - CHANGE PLAYER DATA: \"!l change @name [data type: \'name\', \'score\', \'strikes\', \'all_time_score\', or \'display\'] [insert integer, or name]\" This will change the specified players data type to the user input.```"""
        




def string_to_list(string) -> list:
    # This function takes the users string input and turns it into a list that is easy to read by the other functions in this file.
    
    itemsList = string.strip().split()
    index=0
    while index<len(itemsList):
        if itemsList[index] ==  '':
            itemsList.remove('')
        else:
            index += 1
    
    return itemsList

def get_user_data(discordIds,dataType="all",limit=-1):
    # This function writes to your .txt file to print out the leaderboard information.
    # The discord bot will take the .txt file and print it as an embed into discord.
    # dataType tells the function which columns to grab from the sql table to create a leaderboard.
    # limit is for when the user wants to select the top players or all time top players and lets the function know how many players to grab.
    
    
    
    textFile = "Leaderboard.txt"
    mydb = mysql.connector.connect(
        host = "localhost",
        user = os.getenv("sqlUsername"),
        password = os.getenv("sqlPassword"),
        database = os.getenv("sqlDatabase")
    )
    mycursor = mydb.cursor()

    table = []
    header = []
    dataList =[]
    rank = 0
    prevScore = 65536 #number higher than the largest unsigned small int
    
    if(dataType=="all"):
        header  = ['Player','Weekly Score','All Time Score','Strikes','Discord ID','Displayed? (BOOL)']
        
        for discordId in discordIds:
            mycursor.execute("SELECT discord_name,weekly_score,all_time_score,strikes,discordId,display FROM Leaderboard WHERE discordId = %s",[discordId])
            
            for tuple in mycursor:
                for data in tuple:
                    dataList += [data]
                
                
                table += [dataList]
                dataList=[]
                
    elif(dataType=="in_play"):
        header  = ['Player','Weekly Score','Strikes','Discord ID']
        
        
        mycursor.execute("SELECT discord_name,weekly_score,strikes,discordId FROM Leaderboard WHERE display=1 ORDER BY weekly_score DESC")
        
        for tuple in mycursor:
            for data in tuple:
                dataList += [data]
            
            if(dataList[1]<prevScore):
                prevScore = dataList[1]
                rank+=1
                
            table += [[rank]+dataList]
            dataList=[]
        
    elif(dataType=="weekly+all_time"):
        header  = ['Player','Final Score','New All Time Score','Discord ID']
        
        mycursor.execute("SELECT discord_name,weekly_score,all_time_score,discordId FROM Leaderboard WHERE display=1 ORDER BY weekly_score DESC")
        
        for tuple in mycursor:
            for data in tuple:
                dataList += [data]
            
            if(dataList[1]<prevScore):
                prevScore = dataList[1]
                rank+=1
                
            table += [[rank]+dataList]
            dataList=[]
        
    elif(dataType=="all_time_only"):
        if(limit == -1): #if a limit isn't specified, set limit to 10
            mycursor.execute("SELECT discord_name,all_time_score,discordId FROM Leaderboard ORDER BY all_time_score DESC LIMIT %s",[10])
        else:
            mycursor.execute("SELECT discord_name,all_time_score,discordId FROM Leaderboard ORDER BY all_time_score DESC LIMIT %s",[limit])
        
        header  = ['Player','All Time Score','Discord ID']
        
        for tuple in mycursor:
            for data in tuple:
                dataList += [data]
            
            if(dataList[1]<prevScore):
                prevScore = dataList[1]
                rank+=1
                
            table += [[rank]+dataList]
            dataList=[]
        print(f"table = {table}")
    elif(dataType=="score_only"):
        if(limit == -1): #if a limit isn't specified, set limit to 10
            mycursor.execute("SELECT discord_name,weekly_score,discordId FROM Leaderboard ORDER BY weekly_score DESC LIMIT %s",[10])
        else:
            mycursor.execute("SELECT discord_name,weekly_score,discordId FROM Leaderboard ORDER BY weekly_score DESC LIMIT %s",[limit])
        
        header  = ['Player','Weekly Score','Discord ID']
        
        for tuple in mycursor:
            for data in tuple:
                dataList += [data]
            
            if(dataList[1]<prevScore):
                prevScore = dataList[1]
                rank+=1
                
            table += [[rank]+dataList]
            dataList=[]
        print(f"table = {table}")
    elif(dataType=="new_player"):
        header  = ['New Player','Discord ID']
        
        for discordId in discordIds:
            mycursor.execute("SELECT discord_name,discordId FROM Leaderboard WHERE discordId = %s",[discordId])
            
            for tuple in mycursor:
                for data in tuple:
                    dataList += [data]
                
                table += [dataList]
                dataList=[]
                
        
        
    text = tabulate(table,header,tablefmt="outline")
    f = open(textFile,"w")
    f.write(text)
    f.close()

    return True


def handle_response(message) -> str:
    """
    This function is the first step to your discord bot displaying your leaderboard correctly and calls any functions necessary towards that end based on the discord users input.
    
    bot.py already checks if the first three characters are "!l " so no need to check again.
    We don't want to take a really long string as there should never be a need for an input bigger than 100 chars and we don't want to waste compute power in the string_to_list() function.
    """
    
    if len(message)<500:   
        print("In handle response")
        listInput = string_to_list(message)
        
        if(len(listInput)==1):
            return "OUT:```For help, type \"!l help\" to get a list of commands.```"
        try: #When adding a new player, we don't want to .lower() their name, same with when we change their name
            if(listInput[1].lower()=="add"):
                return add_new_player(listInput[2:]) #working
            elif(listInput[1].lower()=="change" and listInput[3].lower()=="name"):
                return change_attribute(listInput[2:])
        except Exception as e:
            pass    # if the list has fewer than 4 elements 
        
        
        for index,item in enumerate(listInput):
            listInput[index] = item.lower()
        
        
        if(listInput[1]=="q"):
            return get_user_data(listInput[2:])
        elif(listInput[1] == "new_week!"):
            return new_week_update_and_reset()
        elif(listInput[1]=="change"):
            return change_attribute(listInput[2:])
        elif(listInput[1] == "help"):
            return discordUserCommandsList
        elif(listInput[1] == "delete_player"):
            return delete_player(listInput[2])
        elif(listInput[1]=="all_time_top"):
            if(len(listInput)==2):
                return get_user_data(None,"all_time_only")
            try:
                listInput[2] = int(listInput[2])
                return get_user_data(None,"all_time_only",listInput[2])
            except:
                return f"OUT:Please use an int to specify the number of top players you wish to see after \"!l all_time_top\" or leave it blank to see the top ten."
                
        elif(listInput[1]=="top"):
            if(len(listInput)==2):
                return get_user_data(None,"score_only")
            try:
                listInput[2] = int(listInput[2])
                return get_user_data(None,"score_only",listInput[2])
            except:
                return f"OUT:Please use an int to specify the number of top players you wish to see after \"!l top\" or leave it blank to see the top ten."
        elif(listInput[1]=="w" or listInput[1]=="-w" or listInput[1]=="l" or listInput[1]=="-l"):      
            return score_strikes_add_subtract(listInput)
        else:
            print(f"listInput = {listInput}")
            return "OUT: Unrecognized command, use \"!l help\" for the commands list."
      
    else:
        return "OUT:Error: Keep message under 500 Characters."
    

    
def score_strikes_add_subtract(message_items):
    # This function does all the adding and subtracting brought about through the w, -w, l, -l commands
    
    
    mydb = mysql.connector.connect(
        host = "localhost",
        user = os.getenv("sqlUsername"),
        password = os.getenv("sqlPassword"),
        database = os.getenv("sqlDatabase")
    )
    mycursor = mydb.cursor()
    
    

    
    if(message_items[1] == "w"):
        errorDID=[]
        for dID in message_items[2:]:
            
            mycursor.execute("UPDATE Leaderboard SET display=1 WHERE discordId=%s",[dID])
            mydb.commit()
            try:
                mycursor.execute("UPDATE Leaderboard SET weekly_score=weekly_score+1 WHERE discordId=%s",[dID])
                mydb.commit()
            except Exception as e:
                print(e)
                errorDID += [dID]
            
        get_user_data(None,"in_play")
        if(errorDID!=[]):
            stringOut = ""
            for discord_id in errorDID:
                stringOut += f"Warning: {discord_id} has reached max weekly score.\n"
            return stringOut
        
        return True
        
        
    
    if(message_items[1] == "-w"):
        for dID in message_items[2:]:
            
            mycursor.execute("UPDATE Leaderboard SET display=1 WHERE discordId=%s",[dID])
            mydb.commit()
            try:
                mycursor.execute("UPDATE Leaderboard SET weekly_score=weekly_score-1 WHERE discordId=%s",[dID])
                mydb.commit()
            except Exception as e:
                print(e)
            
        
        get_user_data(None,"in_play")
        return True
        
        
    if(message_items[1] == "l"):
        
        stringOut = ""
        for dID in message_items[2:]:
            
            mycursor.execute("UPDATE Leaderboard SET strikes=strikes+1 WHERE discordId=%s and strikes<3",[dID])
            mycursor.execute("UPDATE Leaderboard SET display=1 WHERE discordId=%s",[dID])
            mydb.commit()
            
        mycursor.execute("SELECT discordId FROM Leaderboard WHERE strikes>=3")  # saying >= 3 here is redundant as above strikes +=1 only where strikes<3, but I decided to keep it as I believe it shouldn't add any extra overhead and if something else breaks, its nice to have
        for discord_id in mycursor:
            stringOut += f"Strike 3! {discord_id[0]} you're out!\n"
                
               
            
        get_user_data(None,"in_play")
        
        #Set strikes back to 0 for players in the future
        mycursor.execute("UPDATE Leaderboard SET strikes=0 WHERE strikes=3")
        mydb.commit()
        
        if(stringOut == ""):
            return True
        else:
            return stringOut
        

    if(message_items[1] == "-l"):
        for dID in message_items[2:]:
            
            mycursor.execute("UPDATE Leaderboard SET display=1 WHERE discordId=%s",[dID])
            mydb.commit()
            try:
                mycursor.execute("UPDATE Leaderboard SET strikes=strikes-1 WHERE discordId=%s",[dID])
                mydb.commit()
            except Exception as e:
                print(e)
            
            
        get_user_data(None,"in_play")
        
        return True

def new_week_update_and_reset():
    # This function sets up the players for a new week of playing.
    # It resets weekly scores and strikes after adding the weekly score to the all time score.
    # Lastly, it will prompt get_user_data() to print out the final score and new all time score in the leaderboard organized by top to bottom final scores.
    
    mydb = mysql.connector.connect(
        host = "localhost",
        user = os.getenv("sqlUsername"),
        password = os.getenv("sqlPassword"),
        database = os.getenv("sqlDatabase")
    )
    mycursor = mydb.cursor()
    maxScorers = []
    
    mycursor.execute("SELECT discordId FROM Leaderboard WHERE weekly_score>0")

    discordIds = []
    for discordId in mycursor:
        discordIds += [discordId]
    
    # Sets any rows to visible in case they were set to not display earlier through the change menu
    mycursor.execute("UPDATE Leaderboard SET display=1 WHERE weekly_score>0 and display=0 and strikes>0")
    
    mycursor.execute("UPDATE Leaderboard SET all_time_score=weekly_score+all_time_score WHERE all_time_score+weekly_score<65536 AND display=1")
    mydb.commit()
    mycursor.execute("SELECT discordId FROM Leaderboard WHERE all_time_score+weekly_score>=65535 AND display=1")
    for discordId in mycursor:
        maxScorers += [discordId[0]]

    mycursor.execute("UPDATE Leaderboard SET all_time_score=65535 WHERE all_time_score+weekly_score>65536 AND display=1")
    mydb.commit()
    
    get_user_data(None,"weekly+all_time")
    
    # Reset weekly score
    mycursor.execute("UPDATE Leaderboard SET weekly_score=0 WHERE weekly_score>0")
    # Reset strikes
    mycursor.execute("UPDATE Leaderboard SET strikes=0 WHERE strikes>0")
    # Reset display
    mycursor.execute("UPDATE Leaderboard SET display=0 WHERE display=1")
    mydb.commit()
    
    
    if(maxScorers != []):
        outString = ""
        for x in maxScorers:
            outString += x+" has achieved max all time score!\n"
        return outString
    
    
    return True

def add_new_player(args):
    # This function allows discord users to add new players through discord with the command in the commands list.
    
    mydb = mysql.connector.connect(
        host = "localhost",
        user = os.getenv("sqlUsername"),
        password = os.getenv("sqlPassword"),
        database = os.getenv("sqlDatabase")
    )
    mycursor = mydb.cursor()
    name = ""
    for x in args[1:]:
        name += x+" "
    print(f"name = {name}")
    newPlayerData = (args[0],name.strip(),0,0,0,0)
    
    mycursor.execute("INSERT INTO Leaderboard (discordId, discord_name, weekly_score, all_time_score, strikes, display) VALUES (%s,%s,%s,%s,%s,%s)",newPlayerData)
    mydb.commit()
    
    get_user_data([args[0]],"new_player")
    
    return f"New Player: {name.strip()},{args[0]} added."
    

def delete_player(args):
    # This function allows discord users to delete players through discord with the command in the commands list.
    
    mydb = mysql.connector.connect(
        host = "localhost",
        user = os.getenv("sqlUsername"),
        password = os.getenv("sqlPassword"),
        database = os.getenv("sqlDatabase")
    )
    mycursor = mydb.cursor()
    
    mycursor.execute("SELECT discord_name FROM Leaderboard WHERE discordId = %s",[args])
    
    for x in mycursor:
        name=x[0]
    
    mycursor.execute("DELETE FROM Leaderboard WHERE discordId = %s",[args])
    mydb.commit()

    
    return f"OUT:Deleted player: {name}, {args} from database."

def change_attribute(args):
    # This function allows discord users to change all player data except the discord id of the player as that is the primary key in the sql table, this is done through discord with the command in the commands list.
    
    mydb = mysql.connector.connect(
        host = "localhost",
        user = os.getenv("sqlUsername"),
        password = os.getenv("sqlPassword"),
        database = os.getenv("sqlDatabase")
    )
    mycursor = mydb.cursor()
    
    args[1] = args[1].lower() # We just need to make sure the characters are correct, not the case.
    print("change_attribute")
    print(f"args = {args}")
    
    if(args[1]=="name"):
        
        name=""
        for item in args[2:]:
            name += str(item).strip()+" "
        if(name.strip()==""):
            return f"OUT:Error: {args[0]}'s name cannot be blank."
        
        mycursor.execute("UPDATE Leaderboard SET discord_name=%s WHERE discordId=%s",(name.strip(),args[0]))
        mydb.commit()
        
        get_user_data([args[0]])
        return True
    elif(args[1]=="score"):
        try:
            score = int(args[2])
            if(score<0 or score>256):
                return f"OUT:Error: Please enter a positive integer less than 256 to change {args[0]}'s score."
            mycursor.execute("UPDATE Leaderboard SET weekly_score=%s WHERE discordId=%s",(score,args[0]))
            mycursor.execute("UPDATE Leaderboard SET display=1 WHERE discordId=%s",[args[0]])
            mydb.commit()
            get_user_data(None,"in_play")
            return True
        except Exception as e:
            print(f"OUT:Error: {e}")
            return f"OUT:Error: Please enter a positive integer less than 256 to change {args[0]}'s score."
    elif(args[1]=="strikes" or args[1]=="stirkes"): # I had stirkes as a typo and felt like adding it as a condition lol
        try:
            strikes = int(args[2])
            if(strikes == 3):
                mycursor.execute("UPDATE Leaderboard SET strikes=3 WHERE discordId=%s",[args[0]])
                mydb.commit()
                
                get_user_data(None,"in_play")
                
                mycursor.execute("UPDATE Leaderboard SET strikes=0 WHERE discordId=%s",[args[0]])
                mydb.commit()
                
                return f"Strike 3! {args[0]} you're out!"
                
            
            elif(strikes<0 or strikes>3):
                return f"OUT:Error: Please enter a positive integer less than 4 to change {args[0]}'s strikes."
            else:
                mycursor.execute("UPDATE Leaderboard SET strikes=%s WHERE discordId=%s",(strikes,args[0]))
                mycursor.execute("UPDATE Leaderboard SET display=1 WHERE discordId=%s",[args[0]])
                mydb.commit()
                
                
            
                get_user_data(None,"in_play")
                
                return True
            
            
        except Exception as e:
            print(f"OUT:Error: {e}")
            return f"OUT:Error: Please enter a positive integer less than 4 to change {args[0]}'s strikes."
    elif(args[1]=="all_time_score"):
        try:
            all_time_score = int(args[2])
            if(all_time_score<0 or all_time_score>65535):
                return f"OUT:Error: Please enter a positive integer less than 65536 to change {args[0]}'s All Time Score."
            mycursor.execute("UPDATE Leaderboard SET all_time_score=%s WHERE discordId=%s",(all_time_score,args[0]))
            mydb.commit()
            get_user_data([args[0]])
            return True
        except Exception as e:
            print(f"OUT:Error: {e}")
            return f"OUT:Error: Please enter a positive integer less than 65536 to change {args[0]}'s All Time Score."
    elif(args[1]=="display"):
        try:
            display = int(args[2])
            if(display!=0 and display!=1):
                return f"OUT:Error: Please enter a 0 or a 1 to change {args[0]}'s display."
            mycursor.execute("UPDATE Leaderboard SET display=%s WHERE discordId=%s",(display,args[0]))
            mydb.commit()
            get_user_data([args[0]],"in_play")
            if(display==1):
                return f"{args[0]} has been added to the leaderboard."
            else:
                return f"{args[0]} has been removed from the leaderboard."
        except Exception as e:
            print(f"OUT:Error: {e}")
            return f"OUT:Error: Please enter a 0 or a 1 to change {args[0]}'s display."
    else:
        return f"OUT:Error: Please specify what you would like to change using \"!l change @discordName\" followed by \"name\"|\"score\"|\"all_time_score\"|\"strikes\"|\"display\""

    



