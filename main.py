#read text, and put every word into a list
import string
import re

def read_corpus(file) -> list:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    tokens = content.lower().split()
    clean = []
    for word in tokens:
        token = re.sub(r"[^a-záéíóúüñ]", "", word)
        if token:
            clean.append(token)
    return clean

#we need to count every time a bigram appears
def build_bigram(text:list) -> dict:
    bigram = {}
    #iterate len - 1 of text so we can keep track of the last pair without going out of bounds
    for i in range (len(text) - 1):
        pair = (text[i], text[i + 1])
        #if pair is in bigram + 1
        if pair in bigram:
            bigram[pair] += 1
        #else add bigram
        else:
            bigram[pair] = 1
    return bigram

#function to check the frequency of a pair of words
def check_freq(bigram_list:dict, threshold:int) -> dict|string:
    filtered = {pair:freq for pair, freq in bigram_list.items() if freq >= threshold}
    if filtered:
        return filtered
    return "Theres no bigrams with this frequency"

#check desired word frequency
def check_word(desired_word:str, text:list) -> int|string:
    counter = 0
    for word in text:
        if desired_word == word:
            counter += 1
    return counter

#create vocabulary
def create_vocabulary(text) -> set:
    #set doesn't allow duplicates so its easiers
    words = set()
    for word in text:
        token = re.sub("[^a-záéíóúüñ]", "", word)
        if token:
            words.add(token)
    return words

#create unique words with index
def create_unique_words(text) -> dict:
    dictionary = {word:index for index,word in enumerate(text)}
    return dictionary

#dios: 15651
#dijo: 23534,

if __name__ == "__main__":
    list_of_words = read_corpus("biblia.txt")
    bigram_count = build_bigram(list_of_words)
    #print(check_freq(bigram_count, 500))
    vocab = create_vocabulary(list_of_words)
    #print(create_unique_words(vocab))
    print(check_word("dios", list_of_words))
