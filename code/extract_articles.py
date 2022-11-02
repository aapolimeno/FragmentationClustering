# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 17:53:04 2022

@author: Alessandra
"""

from datasets import load_dataset
import pandas as pd
import trafilatura

def get_text_from_url(url):
    """
    Fetch the HTLM of a link, and extract the text
    
    :param url: string containing the URL to a webpage
    :return: a string containing the full text
    """
    
    processed_text = None
    downloaded = trafilatura.fetch_url(url)
    if type(downloaded) == str: 
        processed_text = trafilatura.extract(downloaded)

    return processed_text


# ============= Load dataset =============

#data = load_dataset('hlgd', script_version="master")
data = load_dataset('hlgd')

# Get train, test and dev sets
hlgd_validation = data['validation']
hlgd_train = data['train']
hlgd_test = data['test']

# Read all data as DataFrame and merge train/test/validation
hlgd_df = pd.DataFrame(hlgd_train)
test = pd.DataFrame(hlgd_test)
validation = pd.DataFrame(hlgd_validation)

hlgd_df = hlgd_df.append(test, ignore_index = True)
hlgd_df = hlgd_df.append(validation, ignore_index = True)

    
# ============= URL extraction =============

# Remove all duplicate URLs, texts have to be extracted only once
urls = hlgd_df['url_a'].tolist()
urlsb = hlgd_df['url_b'].tolist()
for url in urlsb: 
    urls.append(url)
    
unique_urls = list(set(urls))


# Crawl the texts from the urls, save them in a dictionary
# key = url, value = text 

raw_texts = {}
for url in unique_urls: 
    text = get_text_from_url(url)
    raw_texts[url] = [text]

hlgd_texts = pd.DataFrame(raw_texts.items(), columns = ['url', 'text'])

hlgd_texts.to_csv('data/hlgd_texts.csv', index = True)
hlgd_df.to_csv('data/hlgd_pairs.csv', index = True)
