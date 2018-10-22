import pickle

import numpy as np
from nltk.stem import SnowballStemmer


class OneHotEncoder:
    # the modal verbs we will omit
    modal_verbs = ['can', 'could', 'should', 'would', 'may', 'might', 'will', 'would', 'must']
    # random words to be omitted
    irrelevant_word = ['please', 'the']

    # input file containing the training corpus
    input_training_corpus = "trainingCorpus.txt"
    # file containing the stemmed training corpus
    refined_training_corpus = "refinedTrainingData.txt"
    # output file containing the encoded training corpus
    encoded_training_corpus = "encodedTrainingData.txt"
    # contains the used lexicon
    lexicon_pickle_file = 'lexicon.pickle'
    # contains the encoded (final) training corpus
    training_pickle_file = "training_corpus.pickle"

    def __init__(self):
        # will contain all the training entries of type [encoded_sentence : encoded_category]
        self.training_corpus_list = list()
        # will contain all the known words
        self.lexicon = list()
        # the nltk stemmer we use
        self.word_stemmer = SnowballStemmer('english')
        # union of all unwanted words
        self.removable_words = self.modal_verbs + self.irrelevant_word

    def create_refined_training_corpus(self):
        training_content = self.read_entire_file(self.input_training_corpus)

        stemmed_content = list()

        for entry in training_content:
            entry = entry.strip()
            if entry == "":
                continue
            stemmed_entry = self.stem_entry(entry)

            if stemmed_entry not in stemmed_content:
                stemmed_content.append(self.stem_entry(entry))

        self.write_refined_training_data(stemmed_content)

    def create_encoded_training_corpus(self):

        if not self.lexicon:
            self.create_lexicon()

        refined_content = self.read_entire_file(self.refined_training_corpus)

        category_list = list()
        entries = list()
        final_entries = list()

        for entry in refined_content:
            category = entry.split(":")[0].strip()
            sentence = entry.split(":")[1].strip()

            if category not in category_list:
                category_list.append(category)

            encoded_sentence = self.encode_sentence(sentence)

            entries.append([category, encoded_sentence])

        for entry in entries:
            encoded_category = self.encode_category(category_list, entry[0])
            # here we swap from [category, sentence] to [sentence, category]
            final_entries.append([entry[1], encoded_category])

        with open(self.training_pickle_file, 'wb') as file:
            pickle.dump(final_entries, file)
            file.close()

    def encode_category(self, categories_list, category):
        encoded_category = np.zeros(len(categories_list))

        index = categories_list.index(category)
        encoded_category[index] += 1

        return encoded_category

    def load_training_corpus(self):
        with open(self.training_pickle_file, 'rb') as file:
            self.training_corpus_list = pickle.load(file)
            file.close()

    def encode_sentence(self, sentence):

        sentence = self.strip_sentence(sentence)
        sentence = self.stem_sentence(sentence)

        if not self.lexicon:
            self.load_lexicon()

        features = np.zeros(len(self.lexicon))

        for word in sentence.split():
            if word in self.lexicon:
                index_value = self.lexicon.index(word)
                features[index_value] += 1

        return features

    def create_lexicon(self):
        refined_content = self.read_entire_file(self.refined_training_corpus)

        for entry in refined_content:
            sentence = entry.split(":")[1].strip()

            for word in sentence.split():
                if word not in self.lexicon:
                    self.lexicon.append(word)

        with open(self.lexicon_pickle_file, 'wb') as file:
            pickle.dump(self.lexicon, file)
            file.close()

    def load_lexicon(self):
        with open(self.lexicon_pickle_file, 'rb') as file:
            self.lexicon = pickle.load(file)
            file.close()

    def write_refined_training_data(self, content):
        output_file = open(self.refined_training_corpus, 'w')

        [output_file.write("%s : %s\n" % (entry[0], entry[1])) for entry in content]

        output_file.close()

    def read_entire_file(self, file_name):
        input_file = open(file_name, 'r')

        content = input_file.readlines()

        input_file.close()

        return content

    def stem_entry(self, entry):
        # input -> [category: sentence]
        category = entry.split(":")[0].strip()
        sentence = entry.split(":")[1].strip()

        sentence = self.strip_sentence(sentence)
        sentence = self.stem_sentence(sentence)

        return [category, sentence]

    def strip_sentence(self, sentence):
        stripped = sentence.replace('?', '').replace('!', '').replace(',', '')
        return stripped

    def stem_sentence(self, sentence):
        stemmed = ""

        for word in sentence.split():
            if word.lower() not in self.removable_words:
                stemmed += " " + self.word_stemmer.stem(word.lower())

        return stemmed.strip()


if __name__ == '__main__':
    encoder = OneHotEncoder()
    # encoder.create_refined_training_corpus()
    # encoder.create_lexicon()
    # encoder.load_lexicon()
    # encoder.create_encoded_training_corpus()
    # encoder.load_training_corpus()
    # encoder.encode_sentence("Please turn on the light")