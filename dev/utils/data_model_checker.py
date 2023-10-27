import logging

logger = logging.getLogger(__name__)

def check_special_chars(dm): 
    pattern = "\(|\)|\?|/|-"
    results = dm[['Attribute', 'Valid Values']].apply(lambda x: sum(x.str.contains(pattern)))
    print(results)