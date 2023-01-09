import json
from bs4 import BeautifulSoup
import transformers
import datetime
from transformers import pipeline, RobertaTokenizer, RobertaForQuestionAnswering
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from collections import OrderedDict
transformers.logging.set_verbosity_error()

parents = OrderedDict([('Jonas Software', ['Jonas Software', 'Jonas']), ('Vesta Software Group', ['Vesta Software Group', 'Vesta']), ('Volaris Group', ['Volaris Group', 'Volaris']), ('Cultura Technologies', ['Cultura Technologies']), ('Lumine Group', ['Lumine Group', 'Lumine']), ('Trapeze Group', ['Trapeze Group', 'Trapeze', 'Trapeze Software']), ('Harris', ['N. Harris', 'Harris Computer Systems', 'Harris']), ('Constellation Software Inc.', ['constellation software', 'constellation'])])
csuParent = {}
parentNames =[]
for parent, names in parents.items():
    for name in names:
        parentNames.append(name.lower())
parentLinkText = ['jonas', 'vesta', 'volaris', 'csi', 'trapeze', 'lumine', 'cultura', 'harris']
acqTerms = ['acquires', 'acquisition', 'acquisiti', 'joins', 'unite', 'welcomes', 'expands']

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


# def hf_ner(text):
#     ner_tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner")
#     ner_model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner")
#     try:
#         nlp = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer, aggregation_strategy="simple")
#         ner_results = nlp(text)
#         return ner_results
#     except:
#         return None

def parse_articles():
    parsedArticles = []
    for article in articles:
        title = article["title"].lower()
        # if context includes any of the parent companies, add parent company to acquisition object
        # but remove Constellation Software Inc. from the list of parents
        parentsWithoutCSI = {k: v for k, v in parents.items() if k != "Constellation Software Inc."}
        for parent, names in parentsWithoutCSI.items():
            for name in names:
                if f'about {name.lower()}' in article["content"].lower():
                    article["parent"] = parent
                    break
    
        if not article.get("parent"):
            article["parent"] = "Constellation Software Inc."
            print("--> NO PARENT, defaulting to CSI", article["title"])

        # find the link to the target company if it's in article.content
        soup = BeautifulSoup(article["content"], "html.parser")
        for a in soup.find_all("a"):
            url = a.get("href")
            # if url doesn't match any parentLinkText values, save to aquisition object
            if url:
                if not any(parent in url for parent in parentLinkText):
                    article["companyUrl"] = url
        

        text = soup.text
        # find the target acquisition company in the article["content"]
        roberta_answer = hf_roberta(text, "Which company was acquired?") # roberta has best results
        if roberta_answer:
            article["company"] = roberta_answer.strip()
        
            roberta_answer = hf_roberta(text, "When was "+article["company"]+" founded?") # roberta has best results
            if roberta_answer:
                article["companyFounded"] = roberta_answer.strip()

        # find first strong tag with text that includes "About" but does contain any of the values in parents dict arrays
        about_tag = None
        for strong in soup.find_all("b"):
            if "about" in strong.text.lower():
                if not any(parent in strong.text.lower() for parent in parentNames):
                    about_tag = strong.parent
                    break
        if about_tag:
            # find all the following p tags until we find a p tag with a strong inside it
            p_tags = about_tag.find_all_next("p")
            about_paragraphs = []
            for p in p_tags:
                if p.find("b"):
                    break
                else:
                    about_paragraphs.append(p.text)
            article["companyAbout"] = "".join(about_paragraphs)

        # Load article["date"] string which has format "March 02, 2022" into date object and convert to iso format
        try:
            article["date"] = datetime.datetime.strptime(article["date"], "%B %d, %Y").isoformat()
        except:
            print("--> ERROR: could not parse date", article["date"])
        
        del article["content"]
        print(article)
        parsedArticles.append(article)

        # todo use https://opencorporates.com to get founding date and location of target company
    with open('parsedArticles.json', 'w') as f:
        json.dump(parsedArticles, f)

parse_articles()
