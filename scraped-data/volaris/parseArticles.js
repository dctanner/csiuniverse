
// load articles.json file
const cheerio = require("cheerio");
const fs = require("fs");
const { QAClient } = require("question-answering");
const parents = {'Volaris Group': ['Volaris Group', 'Volaris'], 'Cultura Technologies': ['Cultura Technologies'], 'Lumine Group': ['Lumine Group'], 'Trapeze Group': ['Trapeze Group', 'Trapeze'], 'Constellation Software': ['Constellation Software Inc.', 'constellation software']}
const parentLinkText = ['volaris', 'csi', 'trapeze', 'lumine', 'cultura']
const acqTerms = ['acquires', 'acquisition', 'acquisiti', 'joins', 'unite', 'welcomes', 'expands']
const articles = JSON.parse(fs.readFileSync("articles.json"));

async function parseArticles() {
  // count the number of times each word appears in the article.title property
  const wordCount = {};
  for (const article of articles) {
    // split and lowcase words
    const words = article.title.split(" ").map(word => word.toLowerCase().replace(/[^a-z]/g, ''));
    for (const word of words) {
      if (wordCount[word]) {
        wordCount[word]++;
      } else {
        wordCount[word] = 1;
      }
    }
  }
  // sort the words by their number of appearances
  const wordsSorted = Object.keys(wordCount).sort((a, b) => {
    return wordCount[b] - wordCount[a];
  });
  // remove all words with count of less than 5
  const wordsFiltered = wordsSorted.filter(word => wordCount[word] > 5);
  console.log(wordsFiltered)

  const acquisitions = []
  for (const article of articles) {
    const acquisition = {}
    // console.log(article.title);
    const title = article.title.toLowerCase();
    // if title includes any of the parent companies, add parent company to acquisition object
    for (const parent of Object.keys(parents)) {
      for (const name of parents[parent]) {
        if (title.includes(name.toLowerCase())) {
          acquisition.parent = parent;
        }
      }
    }

    if (!acquisition.parent) {
      // Edge cases
      if (title == 'Taranto Systems Limited'.toLowerCase()) {
        acquisition.parent = 'Trapeze Group'
      } else if (title == 'Imperial Prepares for Next Phase of Growth'.toLowerCase()) {
        acquisition.parent = 'Volaris Group'
      } else {
        console.log("NO PARENT", article.title)
      }
    }

    // find the link to the target company if it's in article.content
    console.log(article.link)
    const $ = cheerio.load(article.content);
    for (const el of $("a")) {
      const url = $(el).attr("href");
      // if url doesn't match any parentLinkText values, save to aquisition object
      if (!parentLinkText.some(parent => url.includes(parent))) {
        acquisition.companyUrl = url;
      }
    }

    // use huggingface transformers model bert-large-uncased-whole-word-masking-finetuned-squad to find the target company name in article.contenttokenizer = AutoTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
    const text = $.text();
    const question = "What company was acquired?"
    const qaClient = await QAClient.fromOptions();
    const answer = await qaClient.predict(question, text);
    acquisition.company = answer;

    console.log(acquisition)
  }
}

parseArticles();