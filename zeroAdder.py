#go through LCCN cell
#check if '-' is inside the string
#how many zeroes do you need 8 - len(string)
#iterate through and replace
import pandas as pd
import os.path
from datetime import datetime

def zeroReplace(userfile):
    #Convert CSV file to dataframe
    print(f"Reading {userfile}...")
    df = pd.read_csv(userfile)
    df = df.fillna('')
    try:
        for index, row in df.iterrows():
            LCCN = str(row['LCCN']).strip()
            df.at[index, 'LCCN'] =  ''.join('0'*(8-len(LCCN) + 1) if c == '-' else c for c in LCCN)
        df.to_csv(userfile, index=False)
    except Exception as e:
        raise Exception(e)
    
def welcome():
    #print welcome message & explain steps
    #prompt user for csv file
    #return csv file
    print("*"*32)
    print("* Welcome to Sherman Library's *\n*        LCCN Modifier!        *")
    print("*" + " "*11 + "LCC ed." + " "*12 + "*")
    print("*"*32)
    print("\nPlease have your properly formatted .csv file ready.\n"+
          "There should be LCCN, ISBN, Short Title, Author, and Copyright Year headers.\n"+
          "Each book should have either LCCN, ISBN, or (Short Title, Author, Copyright Year) information\n"+
          "provided for search.\n\n !!IMPORTANT!!\n    Please make sure the .csv is in the same folder as this program."+
         "\n    Please make sure your csv has the necessary headers (LCCN, ISBN, Short Title, Author, Copyright Year).\n"+    
         "\nType 'Quit' to exit the program.")
    print("-"*32 +"\n")

    user_input = input("Please enter the name of your file ( ex: myfile.csv ): ")
    
    while not os.path.isfile(user_input):
        #quit the program if user specifies
        if user_input == "quit" or user_input == "Quit":
            print("Thank you for using the LCCN Modifier. Goodbye.")
            return
        else:
            print(f"Oops! Couldn't find the file {user_input}. Please make sure it is in the same folder as the program, or specify the file's full location"+
                  f" such as 'C:/Documents/myfile.csv'")
            user_input = input("Please enter the name of your file ( ex: 01.30_myfile.csv ) or 'Quit' to quit: ")
    return user_input

def main():
    file_name = welcome()
    try:
        if file_name:
            zeroReplace(file_name)
        print("Processing complete. Please check your file for results. Goodbye.")
    except Exception as e:
        errLOG = open("errorLog.txt", 'a', encoding='utf-8')
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        errLOG.write("{0} | zeroAdder.py: {1}\n".format(timestamp, e))
        errLOG.close()
        print("-"*32 + f"\nThe program encountered an error. Please consult errorLog.txt for details.\n{e}\nPlease try again after troubleshooting. Goodbye.")
        raise SystemExit()

main()
