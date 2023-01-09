# export all parsedArticles.json files in each subdirectory to a single csv file acquisitions.csv
# run this script from the scraped-data directory

import os
import csv
import json

# get the current directory
cwd = os.getcwd()

# create a list of all subdirectories
all_subdirs = [d for d in os.listdir(cwd) if os.path.isdir(d)]
allRows = []
# create a new csv file acquisitions.csv
with open('acquisitions.csv', 'w') as csvfile:
    # create the csv header
    header = ['title', 'link', 'date', 'name', 'parent', 'companyAbout']
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    
    for subdir in all_subdirs:
        json_path = os.path.join(cwd, subdir, 'parsedArticles.json')
        with open(json_path) as f:
            data = json.load(f)
            for article in data:
                # create articleToSave with blank values from header values
                articleToSave = { key: "" for key in header }
                # for each item in header array, check if article has this value and if so write it to the csv file
                for item in header:
                    if item in article:
                        articleToSave[item] = article[item]
                    elif item == "name":
                        if "company" in article:
                            articleToSave[item] = article["company"] 
                        else:
                            articleToSave[item] = ""

                writer.writerow(articleToSave)
                allRows.append(articleToSave)
                
print("acquisitions.csv created!")

print("check data integrity")
print("no record for following parent companies (you should create them manually):")
# look for any rows where the parent cannot be found in the name column
missingParents = []
for row in allRows:
    if row["parent"] not in [r["name"] for r in allRows]:
        if row["parent"] not in missingParents:
            missingParents.append(row["parent"])
            print(row["parent"])