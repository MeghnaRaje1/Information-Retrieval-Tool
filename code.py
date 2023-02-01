''' The file containes three classes
1. InvertedIntex- This is to create and save positional inverted index
2. QuerySearch- This class performs following search operations - Boolean search, Phrase search
    and Proximity search
3. IrRanking - This class calculates Ranked IR based on TFIDF'''

import time
startTime = time.time()
import xml.etree.ElementTree as ET
from stemming.porter2 import stem
import re
import ast
import regex as re
import math
import operator

class InvertedIndex():
    def __init__(self):
        print(" Init Method for creating inverted index")

    def xmlparsing(self):
        ''' This functions read  parse the collection/trec.sample file using Element Tree parcer.
        The output is stored in dictionary format where key is the document id and values are list of words
        from headline and text
        '''
        tree = ET.parse('collections/trec.5000.xml')
        root = tree.getroot()
        self.xmldictionary = {}
        for elem in root:
            for subelem in elem:
                if (subelem.tag == "DOCNO"):
                    DOCNO = subelem.text
                    Head = ""
                    Text = ""
                if (subelem.tag == "HEADLINE"):
                    #print(subelem.text)
                    Head = subelem.text
                if (subelem.tag == "TEXT"):
                    #print(subelem.text)
                    #print("---------")
                    Text = subelem.text
                if (DOCNO != "" and Text != "" and Head != ""):
                    self.xmldictionary[DOCNO] = Head + " " + Text
        print(" XML parsing completed")

    def preprocessing(self):
        '''This function removes anything other than character, number and underscore and replaces it with a
        empty space
        It also converts all upper case characters to lower case
        It also removes stoppword from the tokens
        Stemming also done in this step
    '''
        for doc, lines in self.xmldictionary.items():
            lower_line = lines.lower()
            tokens = re.sub(r'[^\w\s]', ' ', lower_line)
            tokens = tokens.split()
            #print(tokens)
            stopwordlist = []
            with open('englishST.txt', 'r') as f:
                for stopword in f:
                    stopword = stopword.split()
                    stopwordlist.append(stopword[0])
            tokens_without_stop_words = [t for t in tokens if t not in stopwordlist]
            #print(tokens_without_stop_words)

            for i, word in enumerate(tokens_without_stop_words):
                # print(tokens_without_stop_words[word])
                stema = stem(word)
                tokens_without_stop_words[i] = stema
            # print(tokens_without_stop_words)
            self.xmldictionary[doc] = tokens_without_stop_words
        print("Pre-processing completed")

    def creat_index_dictionary(self):
        ''' This function performs the folllowing tasks-
        1. Created flat wordlist to make a dictionary of unique words
        2. Vocabulary is sorted then
        4. Index Dictionary file is created where key is the vocab word and value is again a dictionary
        of document id and vocab position as key value pair'''
        import itertools
        # using itertools
        flat_word_list = list(itertools.chain(*self.xmldictionary.values()))
        print(len(flat_word_list))
        vocab = list(set(flat_word_list))
        vocab.sort()

        self.index_dictionary = {}
        for word in vocab:
            for doc in self.xmldictionary.keys():
                #print("word",word)
                # print("DOC numberd",doc)
                wordlist = self.xmldictionary[doc]
                #print(wordlist)
                if word in wordlist:
                    import numpy as np
                    array = np.array(wordlist)
                    indices = np.where(array == word)[0]
                    index_list_for_doc = []
                    for pos in indices:
                        index_list_for_doc.append(pos)
                    if (word not in self.index_dictionary):
                        self.index_dictionary[word] = {doc: index_list_for_doc}
                    #print(index_dictionary)
                    else:
                        update_dict = {doc: index_list_for_doc}
                        self.index_dictionary[word].update(update_dict)
        print("Positional inverted index created")

    def saving_index_dictionary(self):
        ''' This function saves the index file to a txt document'''
        with open('indexfile.txt', 'w') as f:
            for key, value in self.index_dictionary.items():
                f.write('%s:%s\n' % (key,len(value)))
                for key1,value1 in value.items():
                    f.write('\t%s:%s\n' % (key1,value1))
        with open('indexfiledict.txt', 'w') as f:
            f.write(str(self.index_dictionary))
        print(" Inverted index save to a text file")

class QuerySearch():
    def __init__(self):
        print(" Init Method for query search")

    def load_index_file(self):
        ''' This function load positional inverted index'''
        with (open("indexfiledict.txt", "r")) as openfile:
            res = openfile.readlines()
        self.index_dict_saved = ast.literal_eval(re.search('({.+})', res[0]).group(0))
        print(type(self.index_dict_saved))
        print("Inverted index text file loaded")

    def search_single_term(self,term):
        ''' This function searches for single term in the inverted index dictionary and returns doc accociated
        with those term'''
        term = term.lower()
        term = stem(term)
        index_dict = self.index_dict_saved
        if (term in index_dict.keys()):
            return index_dict[term]
        else:
            print("Term not present", term)

    def evaluatePostfix(self,givenExp):
        ''' This evaluate postfix expression one by one
        The operators are stored in operation stack
        The terms are stored in given stack
        '''

        # Create a stack by taking an empty list which acts
        # as a stack in this case to hold operands (or values).
        givenstack = []
        operationstack = []
        operations = ["AND", "NOT", "OR"]
        doclist = []
        tempdoclist = []
        for key, value in self.index_dict_saved.items():
            for key1, value1 in value.items():
                tempdoclist.append(key1)
        self.totaldoclist=[]
        for doc in tempdoclist:
            self.totaldoclist.append(int(doc))
        self.totaldoclist = set(self.totaldoclist)
        # Traverse the given postfix expression using For loop.
        for word in givenExp:
            # Push the element into the given stack if it is a operator.
            if word not in operations:
                givenstack.append(word)
            else:
                operationstack.append(word)
        topfirstword = givenstack.pop()
        print(topfirstword)
        print(givenstack)
        if not givenstack:
            if operationstack:
                operation = operationstack.pop()
                result1 = self.single_term_query(self.line[1])
                print("operator", operation)
                finalresult=self.totaldoclist-set(result1)
                print(finalresult)
            else:
                finalresult = self.single_term_query(self.line[0])
                print(finalresult)

        else:
            if operationstack and givenstack:
                topsecondword = givenstack.pop()
                print("topsecondword", topsecondword)
                operation = operationstack.pop()
                print("operator", operation)
                if '\"' in topfirstword or '\"' in topsecondword:
                    finalresult=self.phase_and_boolean(topfirstword, topsecondword, operation, operationstack, givenstack)
                else:
                    finalresult=self.boolean_query(topfirstword, topsecondword, operation, operationstack)
            else:
                print(" Operation Stack empty")
                topsecondword = givenstack.pop()
                print(topfirstword)
                print(topsecondword)
                print("======")
                if '\"' in topfirstword and '\"' in topsecondword:
                    finalresult=self.phase_query(topfirstword, topsecondword)

                if '#' in topsecondword:
                    finalresult=self.proximity_query(topfirstword, topsecondword)
        return finalresult

    def phase_query(self,topfirstword, topsecondword):
        ''' This function is used to search for phase query'''
        term1 = re.sub(r'[^\w\s]', '', topfirstword)
        term2 = re.sub(r'[^\w\s]', '', topsecondword)
        result1 = self.search_single_term(term1)
        result2 = self.search_single_term(term2)
        setA = set(result1)
        setB = set(result2)
        result = (setA.intersection(setB))
        finalresult = []
        for val in result:
            for i in result1[val]:
                for j in (result2[val]):
                    if ((int(i) - int(j)) == 1):
                        if val not in finalresult:
                            finalresult.append(val)
        queryresult = []
        for i in finalresult:
            queryresult.append(int(i))
            queryresult.sort()
        print("Final Result after Phase Query", queryresult)
        return queryresult

    def proximity_query(self,topfirstword, topsecondword):
        ''' This function is used for finding proximity between two words'''
        term1 = re.sub(r'[^\w\s]', '', topfirstword)
        proxterm = re.findall(r'\d+', topsecondword)
        term2 = re.sub(r'[^a-zA-Z]', '', topsecondword)
        result1 = self.search_single_term(term1)
        result2 = self.search_single_term(term2)
        setA = set(result1)
        setB = set(result2)
        result = (setA.intersection(setB))
        finalresult = []
        for val in result:
            for i in result1[val]:
                for j in (result2[val]):
                    if (abs(int(i) - int(j)) <= int(proxterm[0])):
                        if val not in finalresult:
                            finalresult.append(val)
        queryresult = []
        for i in finalresult:
            queryresult.append(int(i))
            queryresult.sort()
        print("Final Result after Proximity Query", queryresult)
        return queryresult

    def single_term_query(self,topfirstword):
        ''' This function is used for searching single terms in the index position dictionary
        '''
        result1 = self.search_single_term(topfirstword)
        m2 = []
        for i in result1.keys():
            m2.append(int(i))
            m2.sort()
        return m2

    def boolean_query(self,topfirstword, topsecondword, operation, operationstack):
        ''' This function is used for performing Boolean operation between two terms like AND NOT or AND
        '''
        result1 = self.search_single_term(topfirstword)
        firstwordset = set(result1.keys())
        result2 = self.search_single_term(topsecondword)
        secondwordset = set(result2.keys())
        #     print(firstwordset)
        #     print(secondwordset)
        if (operation == "OR"):
            if operationstack:
                secondoperation = operationstack.pop()
                result = self.totaldoclist - secondwordset
                finalset = list(firstwordset.union(result))
                finalset.sort()
                queryresult = []
                for i in finalset:
                    queryresult.append(int(i))
                queryresult.sort()
                print("Final Result after Boolean Query", queryresult)
            else:
                finalset = list(firstwordset.union(secondwordset))
                finalset.sort()
                queryresult = []
                for i in finalset:
                    queryresult.append(int(i))
                queryresult.sort()
                print("Final Result after Boolean Query", queryresult)
        if (operation == "AND"):
            if operationstack:
                secondoperation = operationstack.pop()
                result = self.totaldoclist - secondwordset
                finalset = list(firstwordset.intersection(result))
                finalset.sort()
                queryresult = []
                for i in finalset:
                    queryresult.append(int(i))
                queryresult.sort()
                print("Final Result after Boolean Query", queryresult)
            else:
                finalset = list(firstwordset.intersection(secondwordset))
                finalset.sort()
                queryresult = []
                for i in finalset:
                    queryresult.append(int(i))
                queryresult.sort()
                print("Final Result after Boolean Query", queryresult)
        if (operation == "NOT"):
            result = self.totaldoclist - firstwordset
            secondoperation = operationstack.pop()
            if (secondoperation == "OR"):
                finalset = list(secondwordset.union(result))
                finalset.sort()
                queryresult = []
                for i in finalset:
                    queryresult.append(int(i))
                queryresult.sort()
                print("Final Result after Boolean Query", queryresult)
            if (secondoperation == "AND"):
                finalset = list(secondwordset.intersection(result))
                finalset.sort()
                queryresult = []
                for i in finalset:
                    queryresult.append(int(i))
                queryresult.sort()
                print("Final Result after Boolean Query", queryresult)
        return queryresult

    def phase_and_boolean(self,topfirstword, topsecondword, operation, operationstack, givenstack):
        ''' This function is used for searching phase and boolean together
        '''
        topthirdword = givenstack.pop()
        if not givenstack:
            if '\"' in topfirstword and '\"' in topsecondword:
                resultprox = self.phase_query(topfirstword, topsecondword)
                resultsingle = self.single_term_query(topthirdword)
            else:
                resultprox = self.phase_query(topsecondword, topthirdword)
                resultsingle = self.single_term_query(topfirstword)
            setB = set(resultprox)
            resultsingleset = set(resultsingle)
            if (operation == "OR"):
                finalset = list(resultsingleset.union(setB))
                finalset.sort()
                queryresult = []
                for i in finalset:
                    queryresult.append(int(i))
                queryresult.sort()
                print("Final Result after Phase and Boolean Query", queryresult)
            if (operation == "AND"):
                finalset = list(resultsingleset.intersection(setB))
                finalset.sort()
                queryresult = []
                for i in finalset:
                    queryresult.append(int(i))
                queryresult.sort()
                print("Final Result after Phase and Boolean Query", queryresult)
            if (operation == "NOT"):
                print("Thirdword",topthirdword)
                print(self.totaldoclist)
                result = self.totaldoclist.difference(resultsingleset)
                resultset=[]
                for i in result:
                    resultset.append(int(i))
                secondoperation = operationstack.pop()
                print(secondoperation)
                print(resultset)
                if (secondoperation == "OR"):
                    finalset = list(setB.union(set(resultset)))
                    finalset.sort()
                    queryresult = []
                    for i in finalset:
                        queryresult.append(int(i))
                    queryresult.sort()
                    print("Final Result after Phase and Boolean Query", queryresult)
                if (secondoperation == "AND"):
                    finalset = list(setB.intersection(set(resultset)))
                    finalset.sort()
                    queryresult = []
                    for i in finalset:
                        queryresult.append(int(i))
                    queryresult.sort()
                    print("Final Result after Phase and Boolean Query", queryresult)
        else:
            topfourthword=givenstack.pop()
            if ('\"' in topfirstword and '\"' in topsecondword) and ('\"' in topthirdword and '\"' in topfourthword):
                resultprox1 = self.phase_query(topfirstword, topsecondword)
                resultprox2 = self.phase_query(topthirdword, topfourthword)
            if (operation == "OR"):
                finalset = list(set(resultprox1).union(set(resultprox2)))
                finalset.sort()
                queryresult = []
                for i in finalset:
                    queryresult.append(int(i))
                queryresult.sort()
                print("Final Result after Phase and Boolean Query", queryresult)
            if (operation == "AND"):
                finalset = list(set(resultprox1).intersection(set(resultprox2)))
                finalset.sort()
                queryresult = []
                for i in finalset:
                    queryresult.append(int(i))
                queryresult.sort()
                print("Final Result after Phase and Boolean Query", queryresult)

        return queryresult

    def parsing_query_file(self):
        ''' This function load executes the queries one by one'''
        with open("queries.boolean.txt", "r") as f1:
            lines = f1.readlines()
            for self.line in lines:
                pattern = ".*" + ':'
                self.line = re.sub(pattern, '', self.line)
                # self.line.strip()
                self.line = self.line.split()
                querynumber=self.line[0]
                print(querynumber)
                self.line= self.line[1:]
                if(len(self.line)==1 and "," in self.line[0]):
                    self.line=self.line[0].split(",")
                print("Starting", self.line)
                result=self.evaluatePostfix(self.line)
                with open('results.boolean.txt', 'a') as f:
                    for doc in result:
                        f.write('%s,%s\n' % (querynumber, doc))
                print("----end----")

class IrRanking():
    def __init__(self):
        print(" Init Method for IR ranking")

    def load_invertex_index(self):
        ''' This method loads inverted index file'''
        with (open("indexfiledict.txt", "r")) as openfile:
            res = openfile.readlines()
        self.index_dict_saved = ast.literal_eval(re.search('({.+})', res[0]).group(0))
        self.stopwordlist = []
        with open('englishST.txt', 'r') as f:
            for self.stopword in f:
                self.stopword = self.stopword.split()
                self.stopwordlist.append(self.stopword[0])

    def search_single_term(self,term):
        term = term.lower()
        term = stem(term)
        index_dict = self.index_dict_saved
        if (term in index_dict.keys()):
            # print(index_dict[term])
            return index_dict[term]
        else:
            print("Term not present", term)


    def scorecalculation(self,query_without_stop_words):
        restdict = {}
        result = {}
        for term in query_without_stop_words[1:]:
            result[term] = self.search_single_term(term)
        for key, val in result.items():
            setA = list((val.keys()))
            for doc in setA:
                score = ((1 + math.log10(len(val[doc]))) * math.log10(5000 / len(val)))
                if doc in restdict:
                    restdict[doc] = restdict[doc] + score
                else:
                    # print(score)
                    restdict[doc] = score

        sorted_d = dict(sorted(restdict.items(), key=operator.itemgetter(1), reverse=True))
        print('Dictionary in descending order by value : ', sorted_d)
        print(len(sorted_d))
        print("-------------end--------")
        counter = 0
        with open('results.ranked.txt', 'a') as f:
            for key, value in sorted_d.items():
                f.write('%s,%s,%s\n' % (query_without_stop_words[0], key, round(value, 4)))
                counter = counter + 1
                if (counter == 150):
                    break

    def ranked_result(self):
        with open("queries.ranked.txt", "r") as f1:
            lines = f1.readlines()
            for line in lines:
                lower_line = line.lower()
                line = re.sub(r'[^\w\s]', ' ', lower_line)
                line = line.split()
                query_without_stop_words = [t for t in line if t not in self.stopwordlist]
                print("QUERY")
                print(query_without_stop_words)
                self.scorecalculation(query_without_stop_words)


if __name__ == '__main__':
    #Index Creation
    invindex=InvertedIndex()
    invindex.xmlparsing()
    invindex.preprocessing()
    invindex.creat_index_dictionary()
    invindex.saving_index_dictionary()

    # Query Search
    queryobj=QuerySearch()
    queryobj.load_index_file()
    queryobj.parsing_query_file()

    #IR Ranking
    irobj=IrRanking()
    irobj.load_invertex_index()
    irobj.ranked_result()
    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))