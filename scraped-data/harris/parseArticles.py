import json
from bs4 import BeautifulSoup
import datetime
from collections import OrderedDict
import torch
import transformers
from transformers import RobertaTokenizer, RobertaForQuestionAnswering
transformers.logging.set_verbosity_error()

parents = OrderedDict([('Jonas Software', ['Jonas Software', 'Jonas']), ('Vesta Software Group', ['Vesta Software Group', 'Vesta']), ('Volaris Group', ['Volaris Group', 'Volaris']), ('Cultura Technologies', ['Cultura Technologies']), ('Lumine Group', ['Lumine Group', 'Lumine']), ('Trapeze Group', ['Trapeze Group', 'Trapeze', 'Trapeze Software']), ('Harris', ['N. Harris', 'N. Harris Computer Corporation', 'N. Harris Computer Corporation (Harris)', 'Harris Computer Systems', 'Harris']), ('Constellation Software', ['constellation software inc.', 'constellation software', 'constellation'])])
parentNames =[]
for parent, names in parents.items():
    for name in names:
        parentNames.append(name.lower())
parentLinkText = ['jonas', 'vesta', 'volaris', 'csi', 'trapeze', 'lumine', 'cultura', 'harris']
acqTerms = ['acquires', 'acquisition', 'acquisiti', 'joins', 'unite', 'welcomes', 'expands']

with open("../csi/parsedArticles.json", "r") as f:
    csiAcqs = json.load(f)
    csiAcqs.reverse() # start with oldest articles so that we can handle subidiaries acquiring subsidiaries

with open("fetchedArticles.json", "r") as f:
    articles = json.load(f)
    articles.reverse() # start with oldest articles so that we can handle subidiaries acquiring subsidiaries

tokenizer = RobertaTokenizer.from_pretrained("deepset/roberta-large-squad2")
model = RobertaForQuestionAnswering.from_pretrained("deepset/roberta-large-squad2")
def hf_roberta(text, question):
    try:
        inputs = tokenizer(question, text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)

        answer_start_index = outputs.start_logits.argmax()
        answer_end_index = outputs.end_logits.argmax()

        predict_answer_tokens = inputs.input_ids[0, answer_start_index : answer_end_index + 1]
        return tokenizer.decode(predict_answer_tokens, skip_special_tokens=True)
    except:
        return None

def parse_articles():
    parsedArticles = []
    for article in articles:
        title = article["title"].lower()
        # if title includes any of the parent companies, add parent company to acquisition object
        newParent = None
        for parent, names in parents.items():
            for name in names:
                if name.lower() in title:
                    newParent = parent
                    break
        if not newParent:
            # if title includes the name of any previous parsedArticles or CSI acqusitions company, it is the parent
            for parsedArticle in parsedArticles:
                # if parsedArticle["company"] is not blank string and is in title
                titleToMatch = parsedArticle["company"].lower().strip()
                if titleToMatch != "" and titleToMatch in title:
                    newParent = parsedArticle["company"]
                    print("--> PARENT FROM PARSED ARTICLES: ", newParent)
                    break
        if not newParent:
            # if title includes the name of any previous CSI acqusitions, it is the parent
            for csiAcq in csiAcqs:
                if csiAcq.get("company"):
                    titleToMatch = csiAcq["company"].lower()
                    # remove all company postfixes like Ltd, Inc., from the titleToMatch
                    for postfix in ["ltd", "inc", "corp", "llc", "plc", "group", "systems", "software"]:
                        titleToMatch = titleToMatch.replace(postfix, "")
                    titleToMatch = titleToMatch.strip()
                    if titleToMatch != "" and titleToMatch in title:
                        newParent = csiAcq["company"]
                        print("--> PARENT FROM CSI ACQ: ", newParent)
                        break
        if not newParent:
            print("--> NO PARENT", article["title"])
        
        article["parent"] = newParent
        # find the link to the target company if it's in article.content
        soup = BeautifulSoup(article["content"], "html.parser")
        for a in soup.find_all("a"):
            url = a.get("href")
            # if url doesn't match any parentLinkText values, save to aquisition object
            if url:
                if not any(parent in url for parent in parentLinkText):
                    article["companyUrl"] = url
        

        # find the target acquisition company in the article["content"]
        question = "Which company was acquired?"
        text = soup.text
        roberta_answer = hf_roberta(text, question) # roberta has best results
        article["company"] = roberta_answer.strip()

        question = "When was "+article["company"]+" founded?"
        text = soup.text
        roberta_answer = hf_roberta(text, question) # roberta has best results
        if roberta_answer:
            article["companyFounded"] = roberta_answer.strip()

        # find first strong tag with text that includes "About" but does contain any of the values in parents dict arrays
        about_tag = None
        for strong in soup.find_all("strong"):
            if "about" in strong.text.lower():
                if not any(parent in strong.text.lower() for parent in parentNames):
                    about_tag = strong
                    break
        if about_tag:
            # find all the following p tags until we find a p tag with a strong inside it
            p_tags = about_tag.find_all_next("p")
            about_paragraphs = []
            for p in p_tags:
                if p.find("strong"):
                    break
                else:
                    about_paragraphs.append(p.text)
            article["companyAbout"] = "".join(about_paragraphs)

        # TODO extract date from article content and convert to iso format
        # article["date"] = FINDDATE.isoformat()
        
        del article["content"]
        print(article)
        parsedArticles.append(article)

        # todo use https://opencorporates.com to get founding date and location of target company
    with open('parsedArticles.json', 'w') as f:
        json.dump(parsedArticles, f)

parse_articles()
