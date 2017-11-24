from nltk.stem import LancasterStemmer

class VocabularyHandler:

    modal_verbs = ['can', 'could', 'should', 'would', 'may', 'might', 'will', 'would', 'must']
    irrelevant_word = ['please', 'the']

    def __init__(self):
        # will contain all the all the dictionaries of type {category : sentence}
        self.sentenceDictList = []
        # will contain all the known words
        self.entireVocabulary = []

    def processTrainingData(self):
        word_stemmer = LancasterStemmer()
        # put together all the unnecessary words in one place
        removable_words = self.modal_verbs + self.irrelevant_word
        inputFile = open("trainingCorpus.txt", "r")

        for line in inputFile:
            # read one line of text at a time
            line = line.strip()
            # ignore empty lines
            if line == "":
                continue
            # split into category and sentence
            category = line.split(":")[0].strip()
            # also, remove "?" and "!" form the string
            sentence = line.split(":")[1].strip().replace('?', '').replace('!', '')

            # remove any modal verb from the sentence
            sentence = " ".join([word for word in sentence.split() if word not in removable_words])

            # split by words -> stem all the words -> reassemble the sentence
            sentence = " ".join([word_stemmer.stem(word) for word in sentence.split()])

            # add the new {category : sentence} pairs into our sentence list
            self.sentenceDictList.append({category: sentence})
            # add all the new words into our vocabulary
            self.entireVocabulary.extend(sentence.split())

        inputFile.close()
        del inputFile

        self.entireVocabulary = (list(set(self.entireVocabulary)))
        self.entireVocabulary.sort()

    def getSentenceDictList(self):
        return self.sentenceDictList

    def getEntireVocabulary(self):
        return self.entireVocabulary

    def createRefinedTrainingDataFile(self):
        outputFile = open("refinedTrainingData.txt", "w")

        for element in self.sentenceDictList:
            outputFile.write(str(element) + "\n")

        outputFile.close()


vocHandler = VocabularyHandler()
vocHandler.processTrainingData()
print()
print("All sentences: %s" % vocHandler.getSentenceDictList())
print()
print("Vocabulary size: %s" % vocHandler.getEntireVocabulary().__len__())
print("All the vocabulary: %s" % vocHandler.getEntireVocabulary())

vocHandler.createRefinedTrainingDataFile()
