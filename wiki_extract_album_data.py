# Download all necessary packages
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import calendar

yrs = np.arange(2014,2018)
starting_url = "https://en.wikipedia.org/wiki/List_of_{}_albums"

for yr in yrs:
    curr_url = starting_url.format(yr)
    print(curr_url)
    
    # get webpage
    page = requests.get(curr_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    wikiTables = soup.find_all(class_="wikitable")
    
    # note: there's an instance for March 7, 2014 that differs in format, so 
    # only extract data from July-December of 2014
    if yr == 2014:
        wikiTables = wikiTables[6:len(wikiTables)]
    
    for wikiTable in wikiTables:
        fileName = "allData/table{}{}.csv"
        rows = wikiTable.find_all('tr')
        colVals = [col.get_text() for col in rows[0].find_all('th')]
    
        # create an empty dataframe
        df = pd.DataFrame(index = np.arange(len(rows)-1), columns = colVals)
        df = df.fillna(0)
    
        # loop through rest of rows
        rows = rows[1:len(rows)]
    
        prev_release_date = 0
        idx = 0
        for row in rows:
            # check if length of columns (td tags) is 7
            # if so, then this row contains release date to be saved
            if len(row.find_all('td')) == 7:
                stats = [stat.get_text() for stat in row.find_all('td')]
                prev_release_date = stats[0]
                df.iloc[idx] = stats
                idx = idx + 1
            else:
                stats = [stat.get_text() for stat in row.find_all('td')]
                stats.insert(0, prev_release_date)
                df.iloc[idx] = stats
                idx = idx + 1
        # remove last column 
        df = df.drop(['Ref.'], axis = 1)  
        
        # remove \n char from release date column and add year to end
        df = df.replace('\n',' ', regex=True)
        df['Release date'] = df['Release date'] + ' ' + yr.astype(str)
        
        # save to csv
        month = prev_release_date.split('\n')[0]
        print(month)
        fileName = fileName.format(month, yr)
        df.to_csv(fileName)
    
df_final = pd.DataFrame(columns = ['Release date', 'Artist', 'Album', 'Genre', 'Label', 'Producer'])

for yr in yrs:
    months = calendar.month_name 
    months = months[1:len(months)]
    if yr == 2014:
        months = months[6:len(months)]
        
    for month in months:
        # open file
        fileName = "allData/table{}{}.csv"
        fileName = fileName.format(month, yr)
        currDf = pd.read_csv(fileName)
        
        # append to df_final
        df_final = df_final.append(currDf, ignore_index = True)
        
# remove last column and put cells with multiple values as a list (genre, label, producer)
df_final = df_final.drop(['Unnamed: 0'], axis = 1) 
colsToFix = ['Genre', 'Label', 'Producer']
rows = np.arange(0,len(df_final))

for col in colsToFix:
    for row in rows:
        if pd.isnull(df_final.iloc[row][col]):
            currList = np.NaN
            #currList = []
            df_final.iloc[row][col] = currList
        else:   
            currList = df_final.iloc[row][col].split(",")
            df_final.iloc[row][col] = currList

## edit release date
#col = ['Release date']
#rows = np.arange(0,len(df_final))
#for c in col:
#    for r in rows:
#        if pd.isnull(df_final.iloc[r][c]):
#            currList = np.NaN
#            #currList = []
#            df_final.iloc[r][c] = currList
#        else:
#            currList = df_final.iloc[r][c].replace(" ","-")
#            df_final.iloc[r][c] = currList
            
# add 'Meta Score' column
scr = 'Meta Score'
df_final[scr] = np.NaN


# save to csv
df_final.to_csv("allData/wikiData.csv", index = False)
        
        
    
        
        
        
        
        
        
        
        
        
        