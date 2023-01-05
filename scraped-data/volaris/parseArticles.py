import json
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

parents = {'Volaris Group': ['Volaris Group', 'Volaris'], 'Cultura Technologies': ['Cultura Technologies'], 'Lumine Group': ['Lumine Group'], 'Trapeze Group': ['Trapeze Group', 'Trapeze'], 'Constellation Software': ['Constellation Software Inc.', 'constellation software']}
parentLinkText = ['volaris', 'csi', 'trapeze', 'lumine', 'cultura']
acqTerms = ['acquires', 'acquisition', 'acquisiti', 'joins', 'unite', 'welcomes', 'expands']

with open("articles.json", "r") as f:
    articles = json.load(f)

def parse_articles():
    acquisitions = []
    for article in articles:
        acquisition = {}
        title = article["title"].lower()
        # if title includes any of the parent companies, add parent company to acquisition object
        for parent, names in parents.items():
            for name in names:
                if name.lower() in title:
                    acquisition["parent"] = parent
                    break
        
        if not acquisition.get("parent"):
            # Edge cases
            if title == "taranto systems limited".lower():
                acquisition["parent"] = "Trapeze Group"
            elif title == "imperial prepares for next phase of growth".lower():
                acquisition["parent"] = "Volaris Group"
            else:
                print("NO PARENT", article["title"])

        # find the link to the target company if it's in article.content
        print(article["link"])
        soup = BeautifulSoup(article["content"], "html.parser")
        for a in soup.find_all("a"):
            url = a.get("href")
            # if url doesn't match any parentLinkText values, save to aquisition object
            if not any(parent in url for parent in parentLinkText):
                acquisition["companyUrl"] = url
        

        # find the target acquisition company in the article["content"]
        tokenizer = AutoTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
        model = AutoModelForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
        question = "What company was acquired?"
        inputs = tokenizer(question, article["content"], return_tensors="tf")
        outputs = model(**inputs)

        answer_start_index = int(tf.math.argmax(outputs.start_logits, axis=-1)[0])
        answer_end_index = int(tf.math.argmax(outputs.end_logits, axis=-1)[0])

        predict_answer_tokens = inputs.input_ids[0, answer_start_index : answer_end_index + 1]
        acquisition["company"] = tokenizer.decode(predict_answer_tokens)
        
        print(acquisition)

parse_articles()
