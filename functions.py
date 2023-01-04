import math as math
import numpy as np
import nltk as nltk
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from googlesearch import search
import urllib
import urllib.request
from urllib.request import urlopen, Request
from trafilatura import fetch_url, extract
from rake_nltk import Rake
from serv import logreg
from typing import Dict, List, Union
import concurrent.futures
nltk.download('stopwords')
nltk.download('punkt')

def getprobabilityofplag(cossim, jacsim):
    y_pred=logreg.predict([[cossim, jacsim], [0,0]])
    y_prob=logreg.predict_proba([[cossim, jacsim], [0,0]])
    prediction = y_pred[0]
    print(prediction)
    percentage = "notplag"
    #IF THE PROBABILITY IS 0.7 OUT OF 1 THEN IT IS PROBABLY PLAGIARISM
    if prediction==1 and y_prob[0][1]>=0.7:
        percentage = math.ceil(y_prob[0][1]*100)
    return percentage

def findkeywords(text, textlang):
    r = Rake(language=textlang)
    r.extract_keywords_from_text(text)
    keywords = r.get_ranked_phrases()
    if len(keywords)>=5:
        keywords = keywords[:5]
    return keywords

def findurls(keywords, language):
    #MAKES QUERY
    urls = []
    for i in keywords:
        query = i
        for result in search(query,lang=language, safe='on', stop=5, pause=1):
            urls.append(result)
    print(urls)
    return urls

def averagesentence(sentence):
    no_stopwords = remove_stopwords(sentence)
    no_stopwords = word_tokenize(no_stopwords)
    new_words= [word for word in no_stopwords if word.isalnum()]
    list = []
    blank = [0 for i in range(300)]
    for i in new_words:
        if language == "english":
            word_vector = model_en.get_word_vector(i)
        if language == "french":
            word_vector = model_fr.get_word_vector(i)
        if language == "spanish":
            word_vector = model_es.get_word_vector(i)
        list.append(word_vector)
    for i in list:
        blank = np.add(blank,i)
    return blank
    for i in range(len(blank)):
        blank[i] = blank[i]/len(new_words)
    return blank

def jaccardsimilarity(student_sentence, internet_sentence):
    text1 = word_tokenize(student_sentence)
    text2 = word_tokenize(internet_sentence)
    text1= [word for word in text1 if word. isalnum()]
    text2= [word for word in text2 if word. isalnum()]
    allwords = []
    intersection = []
    text1allwords = []
    text2allwords = []
    for i in text1:
      text1allwords.append(i)
      if i not in allwords:
        allwords.append(i)
    for i in text2:
      text2allwords.append(i)
      if i not in allwords:
        allwords.append(i)
    for i in text2allwords:
      if i in text1allwords and i not in intersection:
        intersection.append(i)
    jaccardsimilarity = len(intersection)/len(allwords)
    return jaccardsimilarity



def cosinesimilarity(student_sentence, internet_sentence, language):
    avgsent1vec = averagesentence(student_sentence, language)
    avgsent2vec = averagesentence(internet_sentence, language)
    sum = 0
    for i in range(len(avgsent1vec)):
        sum = sum + avgsent1vec[i]*avgsent2vec[i]
    sum1 = 0
    for i in range(len(avgsent1vec)):
        sum1 = sum1 + avgsent1vec[i]**2
    sum1=math.sqrt(sum1)
    sum2 = 0
    for i in range(len(avgsent2vec)):
        sum2 = sum2 + avgsent2vec[i]**2
    sum2=math.sqrt(sum2)
    div = sum1*sum2
    cossim = sum/div
    return cossim



def comparetexts(student_text, internet_text, language):
    #TOKENIZE INTO SENTENCES
    student_sentences = nltk.tokenize.sent_tokenize(student_text)
    internet_sentences = nltk.tokenize.sent_tokenize(internet_text)
    #CREATES ARRAY WHERE THE STUDENT SENTENCE, INTERNET SENTENCE AND THE PROBABILITY OF PLAGIARISM
    sentences_probaplag_link = []
    for i in student_sentences:
        chosen_sentence = []
        probability = 0
        for o in internet_sentences:
            cossim = cosinesimilarity(i, o, language)
            jacsim = jaccardsimilarity(i, o)
            prb = getprobabilityofplag(cossim, jacsim)
            if prb!="notplag":
                if prb>probability:
                    probability = prb
                    chosen_sentence = []
                    chosen_sentence.append([i, o, prb])
            sentences_probaplag_link.append(chosen_sentence)
    if sentences_probaplag_link==[]:
        comparaison_texts = "None"
    if sentences_probaplag_link!=[]:
        comparaison_texts=sentences_probaplag_link
    return comparaison_texts



def gettextsfromurls(urls):
    texts = [[],[]]
    for i in urls :
        downloaded = fetch_url(i)
        if downloaded!=None:
            result = extract(downloaded)
            texts[0].append(result)
            texts[1].append(i)
    return texts



def multiprocessingtexts(bigarray):
    student_text = bigarray[0]
    texts = bigarray[1]
    lang = bigarray[2]
    alltextcomparaisons = []
    for i in texts[0]:
        ind = texts[0].index(i)
        src = texts[1][ind]
        comparaison = comparetexts(student_text, i, lang)
        if comparaison != "None":
            for sent in comparaison:
                sent.append(src)
                alltextcomparaisons.append(sent)
    return alltextcomparaisons

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def findplag(student_text, lang):
    nltk.download('stopwords')
    nltk.download('punkt')
    #TOKENIZE STUDENT TEXT INTO SENTENCES
    student_sentences = nltk.tokenize.sent_tokenize(student_text)
    #FIND KEYWORDS IN THE STUDENT TEXT
    keywords = findkeywords(student_text,lang)
    #FIND ALL THE URLS FROM THE KEYWORDS
    urls = findurls(keywords, lang)
    #MAKES A LIST OF ALL TEXTS BASED ON THE URLS
    texts = gettextsfromurls(urls)
    processes_import_inputs = []
    numoftextsperprocess = (len(texts[0])//10)+1
    textschunks = list(chunks(texts[0], numoftextsperprocess))
    srcchunks = list(chunks(texts[1], numoftextsperprocess))
    for i in range(len(textschunks)):
        processes_import_inputs.append([textschunks[i], srcchunks[i]])
    alltextcomparaisons = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(multiprocessingtexts, [student_text, processes_import_inputs[i], lang]) for i in range(len(processes_import_inputs))]
        for f in concurrent.futures.as_completed(results):
            if len(f.result())>1:
                for o in f.result():
                    alltextcomparaisons.append(o)
            else:
                alltextcomparaisons.append(f.result())


    finalreport = []
    sentnum = 0
    for i in student_sentences:
        #1 student sentence, 2 probability of plag, 3 internet sentence, 4 src
        finalreport.append([i, 0, "", ""])
        for o in alltextcomparaisons:
            #the o array has 4 elements : 1 the original text, 2 the internet sentence, 3 the probability of plag and 4, the src of plag
            if o[0]==i:
                if o[2]>finalreport[sentnum][1]:
                    finalreport[sentnum][1] = o[2]
                    finalreport[sentnum][2] = o[1]
                    finalreport[sentnum][3] = o[3]
        sentnum = sentnum+1
    report = writehtmlreport(finalreport)
    return report

def writehtmlreport(report):
    output_html = "<div class='wrapper'>"
    for i in report:
        if i[1]!=0:
            output_html = output_html + "<div class='jargon-item'> <a href='javascript:void(0)' ng-model='collapsed1' ng-click='collapsed1=!collapsed1'>" + str(i[0]) + "</a>" + "<div class='boxed' ng-show='collapsed1'> Probability of plagiarism of: " + str(i[1]) + "<br>" + "Plagiarism source:" + str(i[3]) + "</div>" + "</div>"
        else:
            output_html = output_html + i[0]
    output_html = output_html + "</div>"
    return output_html

def findwords(text):
    from nltk.corpus import stopwords
    stop = set(stopwords.words("english"))
    words = nltk.word_tokenize(str(text))
    filtered_words = [word.lower() for word in words if word.lower() not in stop]
    new_words= [word for word in words if word.isalnum()]
    return new_words
