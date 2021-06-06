import re
import json
from tqdm import tqdm
from wiki_dump_reader import Cleaner, iterate

from nltk.tokenize import sent_tokenize

database = []
index = {}

prefix = "enwiki"

cleaner = Cleaner()
for title, text in tqdm(iterate(f"./source/{prefix}-latest-pages-articles.xml")):
    text = cleaner.clean_text(text)
    cleaned_text, links = cleaner.build_links(text)
    
    passage = []
    for i in cleaned_text.split("\n"):
        try: 
            if (i[0] == "="):
                break;
            passage.append(i)
        except IndexError:
            break;

    if (len(passage) < 3):
        continue

    result = ""
    for i in passage:
        result = result+i+" "
    result = result.strip()

    if (len(result) < 10):
        continue

    linkdb = []
    for i in links:
        linkdb.append(i["link"])

    splits = sent_tokenize(result)
    front = splits.pop(0)

    result = ""
    for i in splits:
        result = result+i+" "
    result = result.strip()

    database.append({"title": title, "context": result, "target": front, "links": linkdb, "oncontext": True})
    index[title] = front

ldatabase = []
i = 0
for item in tqdm(database, total=len(database)):
    ldatabase.append(item)

    if len(ldatabase) > 53760:
        with open(f"./data/{prefix}-parsed-oc-MD{i}.json", "w") as df:
            df.write(json.dumps(ldatabase))
            ldatabase = []
            i += 1

with open(f"./data/{prefix}-parsed-oc-MD{i}.json", "w") as df:
    df.write(json.dumps(database))
    ldatabase = []
    i += 1

ldatabase = []
i = 0
for item in tqdm(database, total=len(database)):
    try: 
        for link in item["links"]:
            try: 
                ldatabase.append({"title": link, "context": item["context"], "target": index[link], "oncontext": False})
            except KeyError:
                continue
    except KeyError:
        continue

    if len(ldatabase) > 53760:
        with open(f"./data/{prefix}-parsed-oc-OC{i}.json", "w") as df:
            df.write(json.dumps(ldatabase))
            ldatabase = []
            i += 1

with open(f"./data/{prefix}-parsed-oc-OC{i}.json", "w") as df:
    df.write(json.dumps(ldatabase))
    ldatabase = []
    i += 1


breakpoint()



