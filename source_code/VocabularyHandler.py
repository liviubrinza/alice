from nltk.stem import LancasterStemmer, SnowballStemmer


class VocabularyHandler:

    # input file containing the training corpus
    input_TrainingCorpus = "trainingCorpus.txt"
    # output file containing the refined training corpus
    refined_TrainingCorpus = "refinedTrainingData.txt"
    # output file containing the encoded training corpus
    encoded_TrainingCorpus = "encodedTrainingData.txt"
    # the modal verbs we will omit
    modal_verbs = ['can', 'could', 'should', 'would', 'may', 'might', 'will', 'would', 'must']
    # random words to be omitted
    irrelevant_word = ['please', 'the']

    def __init__(self):
        # will contain all the all the dictionaries of type {category : sentence}
        self.trainingDataList = []
        # will contain all the categories from the training data
        self.trainingCategoriesList = []
        # will contain all the dictionaries of type {encoded category : encoded sentence}
        self.encodedDataList = []
        # will contain all the known words
        self.entireVocabulary = list()
        # the nltk stemmer we use
        self.word_stemmer = SnowballStemmer('english')
        # union of all unwanted words
        self.removable_words = self.modal_verbs + self.irrelevant_word
        # the longest sequence of words in the refined sentences
        self.max_words = 0

    def process_sentence(self, inputSentence):
        sentence = inputSentence.replace('?', '').replace('!', '').replace(',', '')
        return_sentence = ""

        for word in sentence.split():
            if word not in self.removable_words:
                return_sentence += " " + self.word_stemmer.stem(word)

        return return_sentence.strip()

    def process_training_data(self):
        set_of_words = set()

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
            sentence = line.split(":")[1].strip()

            # add the category only if it was not yet encountered
            if category not in self.trainingCategoriesList:
                self.trainingCategoriesList.append(category)

            # clean up the sentence -> only keep the necessary information
            sentence = self.process_sentence(sentence)

            # just out of curiosity, save the longest sentence (counting words)
            if len(sentence.split()) > self.max_words:
                self.max_words = len(sentence.split())

            # add the new {category : sentence} pairs into our sentence list
            self.trainingDataList.append({category: sentence})

            # add all the new words into our set of words
            set_of_words.update(sentence.split())

        inputFile.close()
        del inputFile

        self.entireVocabulary = sorted(list(set_of_words))

        # encode all the training data
        for trainingDict in self.trainingDataList:
            # split the elements in the list
            category = next(iter(trainingDict))
            sentence = trainingDict[category]
            # encode both parts
            category = self.get_category_index(category)
            sentence = self.translate_words_to_indexes(sentence.split())
            # append the encoded info
            self.encodedDataList.append({category : sentence})
        # store everything persistently just for comparison sake
        self.create_refined_training_data_file()
        self.create_encoded_training_data_file()

    # translate an input list of words into a list of word indexes from the vocabulary
    def translate_words_to_indexes(self, inputList):
        outputList = list()

        for word in inputList:
            outputList.append(self.get_index_translated_word(word))

        return outputList

    def get_index_translated_word(self, input_word):
        if input_word in self.entireVocabulary:
            return self.entireVocabulary.index(input_word) + 1
        else:
            return 0

    def get_category_index(self, category):
        if category in self.trainingCategoriesList:
            return self.trainingCategoriesList.index(category)
        else:
            return -1

    def get_training_data_list(self):
        return self.trainingDataList

    def get_encoded_data_list(self):
        return self.encodedDataList

    def get_entire_vocabulary(self):
        return self.entireVocabulary

    def get_max_words(self):
        return self.max_words

    def get_categories_list(self):
        return self.trainingCategoriesList

    def create_refined_training_data_file(self):
        outputFile = open(self.refined_TrainingCorpus, "w")
        counter = 0
        for element in self.trainingDataList:
            outputFile.write("%s : %s \n" % (counter, element))
            counter += 1

        outputFile.close()

    def create_encoded_training_data_file(self):
        outputFile = open(self.encoded_TrainingCorpus, "w")
        counter = 0
        for element in self.encodedDataList:
            outputFile.write("%s : %s \n" % (counter, str(element)))
            counter += 1

        outputFile.close()


vocHandler = VocabularyHandler()
vocHandler.process_training_data()
