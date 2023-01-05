import json
from bs4 import BeautifulSoup
import transformers
from transformers import BertTokenizer, BertForQuestionAnswering
import torch        
transformers.logging.set_verbosity_error()

parents = {'Volaris Group': ['Volaris Group', 'Volaris'], 'Cultura Technologies': ['Cultura Technologies'], 'Lumine Group': ['Lumine Group'], 'Trapeze Group': ['Trapeze Group', 'Trapeze'], 'Constellation Software': ['Constellation Software Inc.', 'constellation software']}
parentLinkText = ['volaris', 'csi', 'trapeze', 'lumine', 'cultura']
acqTerms = ['acquires', 'acquisition', 'acquisiti', 'joins', 'unite', 'welcomes', 'expands']

with open("fetchedArticles.json", "r") as f:
    articles = json.load(f)

def hf_roberta(text, question):
    from transformers import RobertaTokenizer, RobertaForQuestionAnswering
    import torch

    tokenizer = RobertaTokenizer.from_pretrained("deepset/roberta-large-squad2")
    model = RobertaForQuestionAnswering.from_pretrained("deepset/roberta-large-squad2")

    inputs = tokenizer(question, text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)

    answer_start_index = outputs.start_logits.argmax()
    answer_end_index = outputs.end_logits.argmax()

    predict_answer_tokens = inputs.input_ids[0, answer_start_index : answer_end_index + 1]
    return tokenizer.decode(predict_answer_tokens, skip_special_tokens=True)

def hf_bert(text, question):
    tokenizer = BertTokenizer.from_pretrained("deepset/bert-large-uncased-whole-word-masking-squad2")
    model = BertForQuestionAnswering.from_pretrained("deepset/bert-large-uncased-whole-word-masking-squad2")      
    inputs = tokenizer(question, text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)       
    answer_start_index = outputs.start_logits.argmax()
    answer_end_index = outputs.end_logits.argmax()      
    predict_answer_tokens = inputs.input_ids[0, answer_start_index : answer_end_index + 1]
    return tokenizer.decode(predict_answer_tokens, skip_special_tokens=True)

def hf_bert_cased(text, question):
    tokenizer = BertTokenizer.from_pretrained("deepset/bert-base-cased-squad2")
    model = BertForQuestionAnswering.from_pretrained("deepset/bert-base-cased-squad2")      
    inputs = tokenizer(question, text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)       
    answer_start_index = outputs.start_logits.argmax()
    answer_end_index = outputs.end_logits.argmax()      
    predict_answer_tokens = inputs.input_ids[0, answer_start_index : answer_end_index + 1]
    return tokenizer.decode(predict_answer_tokens, skip_special_tokens=True)

def parse_articles():
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
        # text = article["title"]
        text = soup.text
        roberta_answer = hf_roberta(text, question) # roberta has best results
        article["company"] = roberta_answer

        print(article)

        # todo use https://opencorporates.com to get founding date and location of target company


parse_articles()
