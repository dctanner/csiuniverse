We scraped the press releases for all OGs to build a complete acquisitions database from the start.

For each folder ing scraped-data, cd in and run the fetchArticles scripts followed by the parseArticles one. Start with csi, as later ones like harris depend on the output of that.

scraped-data/exportToCsv.py then takes all the parsedArticles.json files saves them to acquisitions.csv which we load into Google Sheets which is used as the main db for the application itself.

Then there's a manual cleanup step where we look at all entries with a blank company or parent and manually input these. We do this in Google Sheets.