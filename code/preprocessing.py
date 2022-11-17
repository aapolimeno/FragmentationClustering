# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 13:35:44 2022

@author: Alessandra
"""

import pandas as pd

texts_df = pd.read_csv("data/hlgd_texts.csv", index_col = 0)
pairs_df = pd.read_csv("data/hlgd_pairs.csv", index_col = 0)

urls = texts_df['url'].tolist()


# ================ Extract timeline_ids for each url ================

def extract_timeline_ids(pairs_df): 
    """

    Parameters
    ----------
    pairs_df : TYPE
        DESCRIPTION.

    Returns
    -------
    urls, labels 

    """
    url_a = dict(zip(pairs_df.url_a, pairs_df.timeline_id))
    url_b = dict(zip(pairs_df.url_b, pairs_df.timeline_id))
    
    # Filter duplicats
    urls = []
    labels = []
    
    for k, v in url_a.items(): 
        urls.append(k)
        labels.append(v)
    
    for k, v in url_b.items(): 
        if k not in urls:
            urls.append(k)
            labels.append(v)
    
    return urls, labels

pair_urls, pair_labels = extract_timeline_ids(pairs_df)

# Add to DataFrame         
labels = pd.DataFrame()
labels['url'] = pair_urls
labels['timeline_id'] = pair_labels

# Transpose to create a lookup dictionary
lookup = labels.set_index('url').T.to_dict()

# Find the timeline_id that corresponds to each unique URL in the lookup dict
timeline_ids = []
for url in urls: 
    timeline_id = lookup[url]['timeline_id']
    timeline_ids.append(timeline_id)    

texts_df['timeline_id'] = timeline_ids

# ===================== Extract story chain ids =====================
# Approach 1: split on each timeline and manually look for the pairs 

tl4 = pairs_df.loc[pairs_df['timeline_id'] == 4]
tl4 = tl4[tl4.label == 1]

url_a = tl4['url_a'].tolist()
url_b = tl4['url_b'].tolist()
urls = url_a + url_b

pair = tuple(zip(url_a, url_b))


# Approach 2: Myrthe's dictionary approach
#df = pairs_df[:750]
url_a = list(set(pairs_df['url_a'].tolist()))
url_b = list(set(pairs_df['url_b'].tolist()))

#url_a = set(pairs_df['url_a'].tolist())
#url_b = set(pairs_df['url_b'].tolist())

# all_urls = url_a + url_b



#(len(url_a.intersection(url_b)))


df = pairs_df


chain_dict = {}

for url in url_a: 

    # index = pairs_df.index[pairs_df.url_a == url]
    match_df = df.loc[(df['url_a'] == url) & (df['label'] == 1)]
    match_urls = match_df['url_b'].tolist()
    
    if url not in match_urls: 
        match_urls.append(url)
    
    chain_dict[url] = match_urls
    

chain_df = pd.DataFrame()

links = []
chain_labels = []

for count, chain in enumerate(chain_dict.items()):
    for link in chain[1]:
        if link not in links:
            links.append(link)
            chain_labels.append(count)


    
chain_df['url'] = links
chain_df['story_chain'] = chain_labels


remove_content = ['"', "[", "]"]

# Add text + timeline_id 
texts = []
timeline_ids = []
for link in links: 
    link_df = texts_df.loc[texts_df['url'] == link]
    
    text = link_df['text'].tolist()
    text = str(text)
    text = text.strip("[]''\\")
    text = text.strip('[]""\\')
    text = text.strip("''")
    #text = text.strip("''")
    
    #for content in remove_content:
    #    text = text.replace(content, '')
    
    texts.append(text)
    
    tl_id = link_df['timeline_id'].tolist()
    
    #for t in text: 
    #    t = [t.strip('[]') for i in t]
    #    texts.append(t)

    for tl in tl_id: 
        timeline_ids.append(tl)
    
chain_df['text'] = texts
chain_df['timeline_ids'] = timeline_ids



# Remove stuff 
chain_df = pd.read_csv("data/hlgd_chains.csv", index_col = 0)


### Remove slashes and newlines 
texts = chain_df['text'].tolist()
clean_texts = []

for text in texts: 
    text = text.replace("\\n", "")
    text = text.replace('\\', " ")
    text = text.replace('   ', ' ')
    clean_texts.append(text)
    
chain_df['text'] = clean_texts



### Drop rows with None and CAPTCHA messages 
chain_df = chain_df[chain_df["text"].str.contains("None") == False]
chain_df = chain_df[chain_df["text"].str.contains("To continue, please click the box below") == False]
chain_df = chain_df[chain_df["text"].str.contains("Deze website is geblokkeerd Europese sancties") == False]



#### Remove text after certain keywords 
"""
def remove_after_keyword(df, keyword):

    # identify the to-be-cleaned text
    texts = df["text"].tolist()
    

    
    new_texts = []
    
    for text in texts: 
       # print("old text: ", text)
        old_len = len(text)
        
        #print()
        if keyword in text: 
            index = text.find(keyword)
            text = text[:index]
        #print("new text: ", text)   
        #print(len(text))
        #print()
        new_len = len(text)
        
        if old_len != new_len: 
            print(old_len)
            print(new_len)
            print(keyword)
            print(text)
            print()
        
        new_texts.append(text)

    df['text'] = new_texts
            


keywords = ["VC fund", "Allana"]

for keyword in keywords: 
    remove_after_keyword(chain_df, keyword)

"""


    
chain_df.to_csv("data/hlgd_chains.csv")
