import argparse
import re
import os
import csv
import random
import math


# Stop word list
stopWords = ['a', 'aa', 'ab', 'able', 'about', 'across', 'after', 'all', 'almost', 'also',
			 'am', 'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be',
			 'because', 'been', 'but', 'by', 'can', 'cannot', 'could', 'dear',
			 'did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for',
			 'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers',
			 'him', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is',
			 'it', 'its', 'just', 'least', 'let', 'like', 'likely', 'may',
			 'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor',
			 'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our',
			 'own', 'rather', 'said', 'say', 'says', 'she', 'should', 'since',
			 'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then',
			 'there', 'these', 'they', 'this', 'tis', 'to', 'too', 'twas', 'us',
			 've', 'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which',
			 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet',
			 'you', 'your']

def parseArgument():
    """
    Code for parsing arguments
    """
    parser = argparse.ArgumentParser(description='Parsing a file.')
    parser.add_argument('-d', nargs=1, required=True)
    args = vars(parser.parse_args())
    return args

	# your functions here
def getFileContent(filename):
    """text_list
    retrieve file content
    """
    input_file = open(filename, 'r')
    text = input_file.read()
    input_file.close()
    return text


def AssignProbability(words_dict, posOrNeg):
    uniqueWords = len(words_dict[posOrNeg].keys()) - 1
    totalWords = words_dict[posOrNeg]['totalWordsCounter']
    for key in words_dict[posOrNeg]:
        if(key != 'totalWordsCounter'):
            words_dict[posOrNeg][key]['wordProbability'] = float(words_dict[posOrNeg][key]['wordCount'] + 1)/float(totalWords + uniqueWords + 1)

    return words_dict


def parseFile(words_dict, text, stopWords, posOrNeg):
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\_', ' ', text)
    text = re.sub(r'\d{1,10}', ' ', text)
    text = re.sub(r'a{3,10}', ' ', text)

    text_list = text.split(' ')

    for word in text_list:
        if word == '' or len(word) == 1 or word in stopWords:
            continue
        if word in words_dict[posOrNeg]:
            words_dict[posOrNeg][str(word)]['wordCount'] += 1
            words_dict[posOrNeg]['totalWordsCounter'] += 1
        else:
            words_dict[posOrNeg][str(word)] = {}
            words_dict[posOrNeg][str(word)]['wordCount'] = 1
            words_dict[posOrNeg][str(word)]['wordProbability'] = 0
            words_dict[posOrNeg]['totalWordsCounter'] += 1

    return  words_dict


def writeOutput(words_dict, outputFileName):
    with open(outputFileName, 'wb') as csvfile:
        totalNeg = 0
        for key in words_dict['neg']:
            if(key != 'totalWordsCounter'):
                totalNeg += words_dict['neg'][key]['wordCount']

        totalPos = 0
        for key in words_dict['neg']:
            if(key != 'totalWordsCounter'):
                totalPos += words_dict['neg'][key]['wordCount']

        csvWriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        tempList = ['Class', 'Word', 'Count', 'Probability']
        csvWriter.writerow([x for x in tempList])

        for key in words_dict:
            for word in words_dict[key]:
                if(key == 'neg'):
                    if(word != 'totalWordsCounter'):
                        tempList = [key, word, str(words_dict[key][word]['wordCount']),
                                    str(float(words_dict[key][word]['wordCount'])/float(totalNeg))]
                if(key == 'pos'):
                    if(word != 'totalWordsCounter'):
                        tempList = [key, word, str(words_dict[key][word]['wordCount']),
                                    str(float(words_dict[key][word]['wordCount'])/float(totalPos))]

                csvWriter.writerow([x for x in tempList])

def PopulateWordsDict(words_dict, posOrNeg, directory, trainingFiles):
    for file in trainingFiles:
        text = getFileContent(directory + '\\' + posOrNeg + '\\' + file)
        words_dict = parseFile(words_dict, text, stopWords, posOrNeg)

    words_dict = AssignProbability(words_dict, posOrNeg)
    return words_dict


def DetermineClass(words_dict, testingFiles, directory, posOrNeg):
    final_dict = {}
    for file in testingFiles:
        test_dict = {}
        test_dict['pos'] = {}
        test_dict['neg'] = {}
        test_dict['pos']['totalWordsCounter'] = 0
        test_dict['neg']['totalWordsCounter'] = 0
        text = getFileContent(directory + '\\' + posOrNeg + '\\' + file)
        test_dict = parseFile(test_dict, text, stopWords, posOrNeg)

        negSumProbability = 0
        posSumProbability = 0
        for key in test_dict[posOrNeg]:
            if(key != 'totalWordsCounter'):
                if(key in words_dict['neg'] and key in words_dict['pos']):
                    negSumProbability += float(test_dict[posOrNeg][key]['wordCount'] * math.log(words_dict['neg'][key]['wordProbability']))
                    posSumProbability += float(test_dict[posOrNeg][key]['wordCount'] * math.log(words_dict['pos'][key]['wordProbability']))
                elif(key in words_dict['neg']):
                    negSumProbability += float(test_dict[posOrNeg][key]['wordCount'] * math.log(words_dict['neg'][key]['wordProbability']))
                    posSumProbability += math.log(1/float(words_dict[posOrNeg]['totalWordsCounter'] + len(words_dict['pos'].keys()) + 1))
                elif(key in words_dict['pos']):
                    posSumProbability += float(test_dict[posOrNeg][key]['wordCount'] * math.log(words_dict['pos'][key]['wordProbability']))
                    negSumProbability += math.log(1/float(words_dict[posOrNeg]['totalWordsCounter'] + len(words_dict['neg'].keys()) + 1))
                else:
                    negSumProbability += math.log(1/float(words_dict[posOrNeg]['totalWordsCounter'] + len(words_dict['neg'].keys()) + 1))
                    posSumProbability += math.log(1/float(words_dict[posOrNeg]['totalWordsCounter'] + len(words_dict['pos'].keys()) + 1))

        negProbability = math.log(0.5) + negSumProbability
        posProbability = math.log(0.5) + posSumProbability

        if(negProbability > posProbability):
            final_dict[file] = 'negative'
        else:
            final_dict[file] = 'positive'

    return final_dict

def main():
    for i in range(3):
        args = parseArgument()
        directory = args['d'][0]
        words_dict = {}
        words_dict['pos'] = {}
        words_dict['neg'] = {}
        words_dict['pos']['totalWordsCounter'] = 0
        words_dict['neg']['totalWordsCounter'] = 0

        print('Iteration ' + str(i + 1))

        files = os.listdir(directory + '\\' + 'neg' + '\\')
        trainingFiles = random.sample(files, len(files)*2/3)

        print('num_neg_training_docs:' + str(len(trainingFiles)))

        for index in range(len(trainingFiles)):
            if trainingFiles[index] in files:
                files.remove(trainingFiles[index])
        negTestingFiles = files

        print('num_neg_test_docs:' + str(len(negTestingFiles)))

        words_dict = PopulateWordsDict(words_dict, 'neg', directory, trainingFiles)

        files = os.listdir(directory + '\\' + 'pos' + '\\')
        trainingFiles = random.sample(files, len(files)*2/3)

        print('num_pos_training_docs:' + str(len(trainingFiles)))

        for index in range(len(trainingFiles)):
            if trainingFiles[index] in files:
                files.remove(trainingFiles[index])

        posTestingFiles = files

        print('num_pos_test_docs:' + str(len(posTestingFiles)))

        words_dict = PopulateWordsDict(words_dict, 'pos', directory, trainingFiles)

        final_dict = DetermineClass(words_dict, negTestingFiles, directory, 'neg')

        count = 0
        for key in final_dict:
            if(final_dict[key] == 'negative'):
                count += 1
        print('num_neg_correct_docs:' + str(count))
        print('neg_accuracy:' + str(float(count)/float(len(final_dict.keys()))))

        final_dict = DetermineClass(words_dict, posTestingFiles, directory, 'pos')

        count = 0
        for key in final_dict:
            if(final_dict[key] == 'positive'):
                count += 1
        print('num_pos_correct_docs:' + str(count))
        print('pos_accuracy:' + str(float(count)/float(len(final_dict.keys()))))

main()
