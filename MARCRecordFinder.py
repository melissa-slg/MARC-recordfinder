from bs4 import BeautifulSoup
import csv
import math
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def export_skipped(skipped_list, userfile):
    print(f"Some books were intentionally skipped for manual entry. Please see {userfile[0:5]}_skipped_{len(skipped_list)}.csv for details.")
    print(f"Building {userfile[0:5]}_skipped_{len(skipped_list)}.csv ...")
    pd.DataFrame(skipped_list).to_csv(f'{userfile[0:5]}_skipped_{len(skipped_list)}.csv', index=False)
    print(f"{userfile[0:5]}_skipped_{len(skipped_list)}.csv can now be found in local folder.")
def export_unfound(not_found_list, userfile):    
    print(f"Some books were not found in Library of Congress' records. Please see {userfile[0:5]}_not_found_{len(not_found_list)}.csv for details.")
    print(f"Building {userfile[0:5]}_not_found_{len(not_found_list)}.csv ...")
    pd.DataFrame(not_found_list).to_csv(f'{userfile[0:5]}_not_found_{len(not_found_list)}.csv', index=False)
    print(f"{userfile[0:5]}_not_found_{len(not_found_list)}.csv can now be found in local folder.")
def export_multilink(df, userfile):
    multilink_csv = df.loc[df['Multi-link'] != "" ]
    print(f"Some books require review. Please see {userfile[0:5]}_multilink_{multilink_csv.shape[0]}.csv for details.")
    print(f"Building {userfile[0:5]}_multilink_{multilink_csv.shape[0]}.csv ...")
    pd.DataFrame(multilink_csv).to_csv(f'{userfile[0:5]}_multilink_{multilink_csv.shape[0]}.csv', index=False)
    print(f"{userfile[0:5]}_multilink_{multilink_csv.shape[0]}.csv can now be found in local folder.")

def download_records(userfile):
    webstring = os.getcwd() + "\chromedriver-win64\chromedriver.exe"
    driver = webdriver.Chrome(executable_path=webstring)
    df = pd.read_csv(userfile)
    df = df.fillna('')
    collection_records = open("collection_records.mrc" , 'a', encoding='utf-8')

    #set download directory
    the_options = Options()
    directory_path = os.getcwd()
    the_options.add_experimental_option("prefs", {"download.default_directory": directory_path})
    driver = webdriver.Chrome(options=the_options)
    print("Now collecting MARC records for searched books.")
    
    permalink_count = df['Result Type'].value_counts()['book page']
    i = 0;
    
    driver.get(r"https://catalog.loc.gov/")
    for index, row in df.iterrows():
        permalink = row['Existing LCCN']
        title = row['Short Title']
        if permalink:
            i += 1
            print(f"Acquiring record for {title} (Book {i} of {permalink_count})...")
            try:
                driver.get(permalink)
                time.sleep(10)
                
                #navigate to save page
                save_button = driver.find_element(By.XPATH, "//a[@title='Save the search results']")
                save_button.click()
                time.sleep(2)
                #navigate to download button
                save_button = driver.find_element(By.XPATH, "//button[@title='Save search results']")
                save_button.click()
                time.sleep(10)
                
                #downloads records.mrc
                with open('records.mrc', 'r', encoding='utf-8') as record_file:
                    records = record_file.read()
                collection_records.write(records)
                os.remove(os.path.join(directory_path, 'records.mrc'))
                print(f"    Record obtained for {title} (Book {index+1} of {df.shape[0]}).")
            except Exception as e:
                raise ValueError(e)
        
    driver.quit()
    collection_records.close()
    print("MARC records compiled. Please find collection_records.mrc for details.")       

def full_search(userfile):
    #Convert CSV file to dataframe
    df = pd.read_csv(userfile)
    df = df.fillna('')
    df['Result Type'] = ''
    df['Existing LCCN'] = ''
    df['Multi-link'] = ''
    not_found_list = []
    skipped_list = []
    
    #open new mrc file for appending
    collection_records = open("collection_records.mrc" , 'a', encoding='utf-8')
    
    #set download directory
    the_options = Options()
    directory_path = os.getcwd()
    the_options.add_experimental_option("prefs", {"download.default_directory": directory_path})
    
    try:
        driver = webdriver.Chrome(options=the_options)        
        #search time
        for index, row in df.iterrows():
            lccn = row['LCCN']
            isbn = row['ISBN']
            title = row['Short Title']
            author = row['Author']
            cryear = row['Copyright Year']
            callnum = row['Call No.']
            notes = row['Notes']

            if 'skip' in notes:
                print(f"Special case: Skipping {title}.")
                skipped_list.append({"LCCN": lccn,"ISBN": isbn, "Short Title": title, "Author":author, "Copyright Year":cryear, "Call No.":callnum, "Notes":notes})
            else:
                print(f"Searching for {title} (Book {index+1} of {df.shape[0]})...")
                
                #initiate driver for automated search
                url = 'https://catalog.loc.gov/vwebv/searchAdvanced'
        
                #try each search type
                permalink_text = ""
                found = False
                if lccn: #searching by control number
                    url = f"https://catalog.loc.gov/vwebv/search?searchArg1={lccn}&argType1=all&searchCode1=KNUM&searchType=2&combine2=and&searchArg2=&argType2=all&searchCode2=GKEY&combine3=and&searchArg3=&argType3=all&searchCode3=GKEY&year=1523-2023&fromYear=&toYear=&location=all&place=all&type=all&language=all&recCount=25"   
                    driver.get(url)
                    time.sleep(10)
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    permalink_element = soup.find('a', title='Click to copy permalink for this item')
                    results_bar_element = soup.find('div', class_='results-bar')
            
                    if permalink_element: #direct url exists
                        permalink_text = permalink_element.get_text(strip=True)
                        found = True
                        df.at[index, 'Result Type'] = "book page"
                    elif results_bar_element:
                        df.at[index, 'Multi-link'] = url
                        df.at[index, 'Result Type'] = "multilink"
                        found = True
                        
                if isbn and not found: #searching by isbn
                    url = f"https://catalog.loc.gov/vwebv/search?searchArg1={isbn}&argType1=all&searchCode1=KNUM&searchType=2&combine2=and&searchArg2=&argType2=all&searchCode2=GKEY&combine3=and&searchArg3=&argType3=all&searchCode3=GKEY&year=1523-2023&fromYear=&toYear=&location=all&place=all&type=all&language=all&recCount=25"    
                    driver.get(url)
                    time.sleep(10)
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    permalink_element = soup.find('a', title='Click to copy permalink for this item')
                    results_bar_element = soup.find('div', class_='results-bar')
            
                    if permalink_element: #direct url exists
                        permalink_text = permalink_element.get_text(strip=True)
                        found = True
                        df.at[index, 'Result Type'] = "book page"
                    elif results_bar_element:
                        df.at[index, 'Multi-link'] = url
                        df.at[index, 'Result Type'] = "multilink"
                        found = True
                        
                if not found: #searching by title, author, year
                    url = f"https://catalog.loc.gov/vwebv/search?searchArg1={title}&argType1=all&searchCode1=KTIL&searchType=2&combine2=and&searchArg2={author}&argType2=all&searchCode2=KNAM&combine3=and&searchArg3={cryear}&argType3=all&searchCode3=KPUB&year=1523-2023&fromYear=&toYear=&location=all&place=all&type=all&language=all&recCount=25"
                    driver.get(url)
                    time.sleep(10)
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    permalink_element = soup.find('a', title='Click to copy permalink for this item')
                    results_bar_element = soup.find('div', class_='results-bar')
            
                    if permalink_element: #direct url exists
                        permalink_text = permalink_element.get_text(strip=True)
                        df.at[index, 'Result Type'] = "book page"
                        found = True
                    elif results_bar_element:
                        df.at[index, 'Multi-link'] = url
                        df.at[index, 'Result Type'] = "multilink"
                        found = True
                    else: #book just couldn't be found at all
                        df.at[index, 'Result Type'] = "not found"
                        print(f"    Could not find record for {title}.")
                        not_found_list.append({"LCCN": lccn,"ISBN": isbn, "Short Title": title, "Author":author, "Copyright Year":cryear, "Call No.":callnum, "Notes":notes})

                if permalink_text: #found with one of the three methods
                    df.at[index, 'Existing LCCN'] = permalink_text
                    print(f"    * Record found. Acquiring MARC record.")
                    #add the MARC record to collection_records
                    driver.get(permalink_text)
                    time.sleep(10)
                    #navigate to save page
                    save_button = driver.find_element(By.XPATH, "//a[@title='Save the search results']")
                    save_button.click()
                    time.sleep(2)
                    #navigate to download button
                    save_button = driver.find_element(By.XPATH, "//button[@title='Save search results']")
                    save_button.click()
                    time.sleep(10)
                    #downloads records.mrc
                    with open('records.mrc', 'r', encoding='utf-8') as record_file:
                        records = record_file.read()
                    collection_records.write(records)
                    os.remove(os.path.join(directory_path, 'records.mrc'))
                    print(f"    * Record obtained for {title}.")

        #close browser pages
        driver.quit()
        #convert results to csv
        df.to_csv(userfile, index=False)
        print("Search complete.")
        print("MARC records compiled. Please find collection_records.mrc for details.")       
        
        #construct not_found.csv
        if len(not_found_list) > 0:
            export_unfound(not_found_list, userfile)
        if len(skipped_list) > 0:
            export_skipped(skipped_list, userfile)
        if len(df[df['Result Type'] == 'multilink']) > 0:
            export_multilink(df, userfile)
    except Exception as e:
        print("#### Error encountered. The program is attempting to save your work. ####")
        df.to_csv(userfile, index=False)
        if len(not_found_list) > 0:
            export_unfound(not_found_list, userfile)
        if len(skipped_list) > 0:
            export_skipped(skipped_list, userfile)
        raise ValueError(e)
def welcome():
    #print welcome message & explain steps
    #prompt user for csv file
    #return csv file
    print("*"*32)
    print("* Welcome to Sherman Library's *\n*      MARC Record Finder!     *")
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
            print("Thank you for using the MARC Record Finder. Goodbye.")
            return
        else:
            print(f"Oops! Couldn't find the file {user_csv}. Please make sure it is in the same folder as the program, or specify the file's full location"+
                  f" such as 'C:/Documents/myfile.csv'")
            user_input = input("Please enter the name of your file ( ex: 01.30_myfile.csv ) or 'Quit' to quit: ")
    return user_input
def main():
    try:
        user_csv = welcome()
        if user_csv:
            full_search(user_csv)
            print("-"*32 + f"\nThank you for waiting! Record Finder has finished traversing {user_csv}. Please check your folder for results.\n" + "-"*32)
            #download_records(user_csv)
            print("Thank you for using the MARC record finder. Goodbye.")
    except Exception as e:
        print("-"*32 + f"\nThe program encountered an error. Please consult the details below.\n{e}\nPlease try again after troubleshooting. Goodbye.")
        
    

main()
