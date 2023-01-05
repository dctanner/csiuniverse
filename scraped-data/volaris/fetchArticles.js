const fs = require("fs");
const axios = require("axios");
const cheerio = require("cheerio");

const output = [];

async function fetchArticles() {
  const jsonRes = fs.readFileSync("articleLinks.json");
  const htmlObj = cheerio.load(JSON.parse(jsonRes).response.join(''));

  for (const el of htmlObj("article")) {
    const link = htmlObj(el).find("a.uf-tile").attr("href");
    const title = htmlObj(el).find("h1.title").text().trim();
    const date = htmlObj(el).find("span.js-readable-timestamp").attr("datetime");

    try {
      const response = await axios.get(link);
      const $ = cheerio.load(response.data);
      const content = $("#uf-item-entry-content").html();
      output.push({ link, title, date, content });
      console.log("SUCCESS", link, title, date);
    } catch (error) {
        console.log("ERROR", error, link, title, date);
    }
  }
  // save output to file
  fs.writeFileSync("articles.json", JSON.stringify(output));
}

fetchArticles();