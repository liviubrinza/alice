from nltk.stem import LancasterStemmer


class VocabularyHandler:

    # input file containing the training corpus
    input_TrainingCorpus = "trainingCorpus.txt"
    # output file containing the refined training corpus
    refined_TrainingCorpus = "refinedTrainingData.txt"
    # the modal verbs we will omit
    modal_verbs = ['can', 'could', 'should', 'would', 'may', 'might', 'will', 'would', 'must']
    # random words to be omitted
    irrelevant_word = ['please', 'the']

    def __init__(self):
        # will contain all the all the dictionaries of type {category : sentence}
        self.trainingDataList = []
        # will contain all the known words
        self.entireVocabulary = set()
        self.word_stemmer = LancasterStemmer()
        self.removable_words = self.modal_verbs + self.irrelevant_word
        # the longest sequence of words in the refined sentences
        self.max_words = 0

    def processSentence(self, inputSentence):
        return_sentence = ""

        for word in inputSentence.split():
            if word not in self.removable_words:
                return_sentence += " " + self.word_stemmer.stem(word)

        return return_sentence.strip()

    def processTrainingData(self):

        # put together all the unnecessary words in one place
        inputFile = open(self.input_TrainingCorpus, "r")

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

            sentence = self.processSentence(sentence)

            # just out of curiosity, save the longest sentence (counting words)
            if len(sentence.split()) > self.max_words:
                self.max_words = len(sentence.split())

            # add the new {category : sentence} pairs into our sentence list
            self.trainingDataList.append({category: sentence})
            # add all the new words into our vocabulary
            self.entireVocabulary.update(sentence.split())

        inputFile.close()
        del inputFile

    def getTrainingDataList(self):
        return self.trainingDataList

    def getEntireVocabulary(self):
        return sorted(self.entireVocabulary)

    def getMaxWords(self):
        print("Max words count: %s" % self.max_words)
        #return self.max_words

    def createRefinedTrainingDataFile(self):
        outputFile = open(self.refined_TrainingCorpus, "w")

        for element in self.trainingDataList:
            outputFile.write(str(element) + "\n")

        outputFile.close()


vocHandler = VocabularyHandler()
vocHandler.processTrainingData()
print()
print("All sentences: %s" % vocHandler.getTrainingDataList())
vocHandler.getMaxWords()
print()
print("Vocabulary size: %s" % vocHandler.getEntireVocabulary().__len__())
print("All the vocabulary: %s" % vocHandler.getEntireVocabulary())


vocHandler.createRefinedTrainingDataFile()
