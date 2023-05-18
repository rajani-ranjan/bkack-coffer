# importing the library that we required

import numpy as np
import re
# import os
import pandas as pd 
from nltk.tokenize import RegexpTokenizer, sent_tokenize
from urllib.request import urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests



stop_word_file = './StopWords/StopWords_Generic.txt'

positive_words_file = './MasterDictionary/positive-words.txt'

negative_word_file = './MasterDictionary/negative-words.txt'

pd.set_option('display.max_colwidth', None)
input = pd.read_excel('./Input.xlsx')

urls = input['URL']

# Extrecting article title and article text from teh URLs of the data using BeautifulSoup 

titles = []
text = []
for url in urls:
    
    page = requests.get(url, headers = {"User-Agent":"XY"})
    soup = BeautifulSoup(page.text , 'html.parser')

    try:
        s_title = soup.find('h1').get_text()
    except Exception:
        s_title = ""
    
    titles.append(s_title)
    
    try:
        s_text = soup . find(attrs = { 'class' : 'td-post-content'}).get_text()
    except Exception:
        s_text = ""
    
    text.append(s_text)

'''
## Cleaning article texts using Stop Words Lists
The Stop Words Lists (found in the folder StopWords) are used to clean the text so that Sentiment Analysis can be performed by excluding the words found in Stop Words List. 
* removing the stop words (using stopwords class of nltk package).
* removing any punctuations like ? ! , . from the word before counting.
'''

clean_text = []
for i in range(len(text)):
    clean_text.append(text[i].replace('\n', ' '))

# Save the extracted article title and article text in a text file with URL_ID as its file name.
for i in range(len(clean_text)):
    with open(r"./text_files/"+str(input.URL_ID[i])+".txt", "w", encoding="utf-8" ) as file:

        file.write(titles[i] + "\n" +clean_text[i])




with open(positive_words_file, "r") as pos_file:
    positive_words = pos_file.read().lower()
positive_word_list = positive_words.split('\n')

with open(negative_word_file, 'r', encoding="ISO-8859-1") as neg_file:
    negative_words= neg_file.read().lower()
negative_word_list = negative_words.split('\n')

with open(stop_word_file,'r') as stop_word_file:
    stop_words = stop_word_file.read().lower()
stop_word_list = stop_words.split('\n')

def Tokenizer(text):
    text = text.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    filtered_words = list(filter(lambda token: token not in stop_word_list, tokens))
    return filtered_words
'''
## Data Analysis
For each of the extracted texts from the article, perform textual analysis and compute variables, given in the output structure excel file. 
'''

words_list = []  
for i in range(len(clean_text)):
    word = Tokenizer(clean_text[i])
    words_list.append(word)

'''
## Word Count
#### We count the total number of cleaned words present in the text
'''
words_count = []
for i in range(len(words_list)):
    word_count = len(words_list[i])
    words_count.append(word_count)

'''
### Positive Score: 
This score is calculated by assigning the value of +1 for each word if found in the Positive Dictionary and then adding up all the values.
'''

positive_score=[] 
for i in range(len(words_list)):
    pos_word = 0
    for word in words_list[i]:
        if word in positive_word_list:
            pos_word +=1
    positive_score.append(pos_word)


'''
## Negative Score: 
This score is calculated by assigning the value of -1 for each word if found in the Negative Dictionary and then adding up all the values. We multiply the score with -1 so that the score is a positive number.
'''

negative_score=[] 
for i in range(len(words_list)):
    neg_word = 0
    for word in words_list[i]:
        if word in negative_word_list:
            neg_word +=1
    negative_score.append(neg_word)

'''
## Polarity Score: 
This is the score that determines if a given text is positive or negative in nature. It is calculated by using the formula: 
### Polarity Score = 
(Positive Score – Negative Score)/ ((Positive Score + Negative Score) + 0.000001)
'''

polarity_score = []
for i in range(len(positive_score)):
    pol_score = (positive_score[i] - negative_score[i])/((positive_score[i] + negative_score[i])+0.000001)
    polarity_score.append(pol_score)

'''
## Subjectivity Score:
 This is the score that determines if a given text is objective or subjective. It is calculated by using the formula: 
### Subjectivity Score = 
(Positive Score + Negative Score)/ ((Total Words after cleaning) + 0.000001)
'''

subjectivity_score = []
for i in range(len(positive_score)):
    sub_score = ((positive_score[i] + negative_score[i])/ ((words_count[i]) + 0.000001))
    subjectivity_score.append(sub_score)

# Counting sentences in the Article
sentence_count=[]
for i in range(len(clean_text)):
    sentences =  len(sent_tokenize(clean_text[i]))
    sentence_count.append(sentences)

'''
## Analysis of Readability
Analysis of Readability is calculated using the Gunning Fox index formula described below.
#### Average Sentence Length = the number of words / the number of sentences
'''

average_sentence_lenght=[]
for i in range(len(words_count)):
    sent_count = sentence_count[i]
    if sent_count > 0 : 
        avg_sent_len = round(words_count[i] / sentence_count[i])
        average_sentence_lenght.append(avg_sent_len)
    else:
        avg_sent_len = 0
        average_sentence_lenght.append(avg_sent_len)


'''
### Complex Word Count
#### Complex words are words in the text that contain more than two syllables.
'''
complex_word_count =[]
for i in range(len(words_list)):
    complexWord = 0

    for word in words_list[i]:
        vowels=0
        if word.endswith(('es','ed')):
            pass
        else:
            for w in word:
                if(w=='a' or w=='e' or w=='i' or w=='o' or w=='u'):
                    vowels += 1
            if(vowels > 2):
                complexWord += 1
    complex_word_count.append(complexWord)


'''
#### Percentage of Complex words = the number of complex words / the number of words 
'''

complex_word_percentage = []

for i in range(len(words_count)):
    if words_count[i] > 0 :
        comp_word_percent = complex_word_count[i]/words_count[i]
        
    else:
        comp_word_percent = 0
    complex_word_percentage.append(comp_word_percent)

'''
#### Fog Index = 0.4 * (Average Sentence Length + Percentage of Complex words)
'''

fog_index = []
for i in range(len(average_sentence_lenght)):
    fogIndex = 0.4 * (average_sentence_lenght[i] + complex_word_percentage[i])
    fog_index.append(fogIndex)


'''
## Syllable Count Per Word
#### We count the number of Syllables in each word of the text by counting the vowels present in each word. We also handle some exceptions like words ending with "es","ed" by not counting them as a syllable.
'''

syllable_count = []
for i in range(len(words_list)):
    count = 0
    for j in range(len(words_list[i])):        
        vowels = 'aeiouy'
        word = words_list[i][j].strip(".:;?!")
        if word[0] in vowels:
            count +=1
        for index in range(1,len(word)):
            if word[index] in vowels and word[index-1] not in vowels:
                count +=1
        if word.endswith('es'):
            count -= 1
        elif word.endswith('ed'):
            count-=1
        elif count == 0:
            count +=1
    syllable_count.append(count)


'''
## Personal Pronouns
#### To calculate Personal Pronouns mentioned in the text, we use regex to find the counts of the words - “I,” “we,” “my,” “ours,” and “us”. Special care is taken so that the country name US is not included in the list.
'''

presonal_pronoun = []
for i in range(len(clean_text)):
    pronounRegex = re.compile(r'I|we|my|ours|us',re.I)
    pronouns = pronounRegex.findall(clean_text[i])
    presonal_pronoun.append(len(pronouns))

'''
## Average Word Length
##### Average Word Length is calculated by the formula:
Sum of the total number of characters in each word/Total number of words
'''

char_count=[]
for i in range(len(clean_text)):
    char = clean_text[i].replace(' ', '')
    char = len(char)
    char_count.append(char)


avg_word_len = []
for i in range(len(char_count)):
    if words_count[i] == 0 | char_count[i]==0 :
        AWC = 0
        avg_word_len.append(AWC)
    else:
        AWC = char_count[i]/words_count[i]
        avg_word_len.append(round(AWC))

'''
Output Data Structure
Output Variables: 
All input variables in “Input.xlsx”
* POSITIVE SCORE
* NEGATIVE SCORE
* POLARITY SCORE
* SUBJECTIVITY SCORE
* AVG SENTENCE LENGTH
* PERCENTAGE OF COMPLEX WORDS
* FOG INDEX
* AVG NUMBER OF WORDS PER SENTENCE
* COMPLEX WORD COUNT
* WORD COUNT
* SYLLABLE PER WORD
* PERSONAL PRONOUNS
* AVG WORD LENGTH
'''

input['POSITIVE SCORE'] = positive_score
input['NEGATIVE SCORE'] = negative_score
input['POLARITY SCORE'] = polarity_score
input['SUBJECTIVITY SCORE'] = subjectivity_score
input['AVG SENTENCE LENGTH'] = average_sentence_lenght
input['PERCENTAGE OF COMPLEX WORDS'] = complex_word_percentage
input['FOG INDEX'] = fog_index
input['AVG NUMBER OF WORDS PER SENTENCE'] = average_sentence_lenght
input['COMPLEX WORD COUNT'] = complex_word_count
input['WORD COUNT'] = words_count
input['SYLLABLE PER WORD'] = syllable_count
input['PERSONAL PRONOUNS'] = presonal_pronoun
input['AVG WORD LENGTH'] = avg_word_len

# Now we have to save the output in the exact order as given in the output structure file, “Output Data Structure.xlsx”
# All input variables in “Input.xlsx”
input.to_excel("Output_Data_Structure.xlsx")