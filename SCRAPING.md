We scraped the press releases for all OGs to build a complete acquisitions database from the start.

See scraped-data folder for our raw output. These results are then loaded into an SQlite db, before the info we want is extract from the press release text.

## Volaris

Has a JSON API which returns all news in one req: https://explore.volarisgroup.com/themes/tiles/collection/8737532?excludeCTAs=false&format=html&infiniteScroll=false&limit=20&page=3

parseArticles.py needs to run on a GPU machine.