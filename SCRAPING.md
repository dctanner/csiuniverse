We scraped the press releases for all OGs to build a complete acquisitions database from the start.

For each folder ing scraped-data, cd in and run the fetchArticles scripts followed by the parseArticles one. Start with csi, as later ones like harris depend on the output of that.

scraped-data/exportToCsv.py then takes all the parsedArticles.json files saves them to acquisitions.csv which we load into Google Sheets which is used as the main db for the application itself.

Then there's a manual cleanup step where we look at all entries with a blank company or parent and manually input these. We do this in Google Sheets.

# Manual changes log
Some of the more major changes to the csv are listed here, but futher tweaks will only be recorded in the Google Sheet.

- Add missing parent records as output by exportToCsv.py
- Add Vela, formed https://www.csisoftware.com/category/press-releases/2019/01/22/constellation-software-announces-executive-appointments "The Vela Software Group is a combination of the Friedman and Emphasys operating groups."
- Many check the records from csisoftware.com, as many have CSI incorrectly set as the parent