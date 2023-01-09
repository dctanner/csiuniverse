import json
from bs4 import BeautifulSoup
import transformers
import datetime
from transformers import RobertaTokenizer, RobertaForQuestionAnswering
import torch
transformers.logging.set_verbosity_error()

parents = {'Jonas Software': ['Jonas Software', 'Jonas'], 'Vesta Software Group': ['Vesta Software Group', 'Vesta'], 'Volaris Group': ['Volaris Group', 'Volaris'], 'Cultura Technologies': ['Cultura Technologies'], 'Lumine Group': ['Lumine Group', 'Lumine'], 'Trapeze Group': ['Trapeze Group', 'Trapeze'], 'Constellation Software': ['Constellation Software Inc.', 'constellation software']}
parentNames =[]
for parent, names in parents.items():
    for name in names:
        parentNames.append(name.lower())
parentLinkText = ['jonas', 'vesta', 'volaris', 'csi', 'trapeze', 'lumine', 'cultura']
acqTerms = ['acquires', 'acquisition', 'acquisiti', 'joins', 'unite', 'welcomes', 'expands']

with open("fetchedArticles.json", "r") as f:
    articles = json.load(f)

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
        for parent, names in parents.items():
            for name in names:
                if name.lower() in title:
                    article["parent"] = parent
                    break
        
        if not article.get("parent"):
            # Edge cases
            if title == "taranto systems limited".lower():
                article["parent"] = "Trapeze Group"
            elif title == "imperial prepares for next phase of growth".lower():
                article["parent"] = "Volaris Group"
            else:
                print("NO PARENT", article["title"])

        # find the link to the target company if it's in article.content
        soup = BeautifulSoup(article["content"], "html.parser")
        for a in soup.find_all("a"):
            url = a.get("href")
            # if url doesn't match any parentLinkText values, save to aquisition object
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

        # Load article["date"] string which has format "MMM DD, YYYY" into date object and convert to iso format
        article["date"] = datetime.datetime.strptime(article["date"], "%b %d, %Y").isoformat()
        
        del article["content"]
        print(article)
        parsedArticles.append(article)

        # todo use https://opencorporates.com to get founding date and location of target company
    with open('parsedArticles.json', 'w') as f:
        json.dump(parsedArticles, f)

parse_articles()
