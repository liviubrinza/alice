import numpy as np
from FileHandler import FileHandler
from nltk.stem import SnowballStemmer

class OneHotEncoder:
    # the modal verbs we will omit
    modal_verbs = ['can', 'could', 'should', 'would', 'may', 'might', 'will', 'would', 'must']
    # random words to be omitted
    irrelevant_word = ['please', 'the']

    def __init__(self):
        # will contain all the training entries of type [encoded_sentence : encoded_category]
        self.training_corpus_list = list()
        # will contain all the known words
        self.lexicon = list()
        self.categories = list()
        # the nltk stemmer we use
        self.word_stemmer = SnowballStemmer('english')
        # union of all unwanted words
        self.removable_words = self.modal_verbs + self.irrelevant_word
        self.file_handler = FileHandler()

    def create_refined_training_corpus(self):
        training_content = self.file_handler.read_training_corpus()
        stemmed_content = list()

        for entry in training_content:
            entry = entry.strip()
            if entry == "":
                continue
            stemmed_entry = self.stem_entry(entry)

            if stemmed_entry not in stemmed_content:
                stemmed_content.append(stemmed_entry)

        refined_training_data_list = [entry[0] + " : " + entry[1] for entry in stemmed_content]
        self.file_handler.write_refined_training_corpus(refined_training_data_list)

    def create_encoded_training_corpus(self):
        if not self.lexicon:
            self.create_lexicon()

        refined_content = self.file_handler.read_refined_training_corpus()

        category_list = list()
        entries = list()
        final_entries = list()

        for entry in refined_content:
            split_content = entry.split(":")
            category = split_content[0].strip()
            sentence = split_content[1].strip()

            if category not in category_list:
                category_list.append(category)

            encoded_sentence = self.encode_sentence(sentence)

            entries.append([category, encoded_sentence])

        for entry in entries:
            encoded_category = self.encode_category(category_list, entry[0])
            # here we swap from [category, sentence] to [sentence, category]
            final_entries.append([entry[1], encoded_category])

        self.categories = category_list
        self.training_corpus_list = final_entries
        self.file_handler.write_training_pickle(final_entries)

    def encode_category(self, categories_list, category):
        encoded_category = np.zeros(len(categories_list))

        index = categories_list.index(category)
        encoded_category[index] += 1

        return encoded_category

    def encode_sentence(self, sentence):
        sentence = self.strip_sentence(sentence)
        sentence = self.stem_sentence(sentence)

        if not self.lexicon:
            self.file_handler.read_lexicon_pickle()

        features = np.zeros(len(self.lexicon))

        for word in sentence.split():
            if word in self.lexicon:
                index_value = self.lexicon.index(word)
                features[index_value] += 1

        return features

    def create_lexicon(self):
        refined_content = self.file_handler.read_refined_training_corpus()

        for entry in refined_content:
            sentence = entry.split(":")[1].strip()

            for word in sentence.split():
                if word not in self.lexicon:
                    self.lexicon.append(word)

        self.file_handler.write_lexicon_pickle(self.lexicon)

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

    def pickle_entire_data(self):
        if self.lexicon is not None and self.training_corpus_list is not None:
            self.file_handler.write_vocabulary_data_pickle([self.lexicon, self.categories, self.training_corpus_list])

    def load_entire_data_from_pickle(self):
        self.lexicon, self.categories, self.training_corpus_list = self.file_handler.read_vocabulary_data_pickle()

    def load_data(self):
        if not self.file_handler.vocabulary_data_pickle_exists():
            self.create_refined_training_corpus()
            self.create_lexicon()
            self.create_encoded_training_corpus()
            self.pickle_entire_data()

        self.load_entire_data_from_pickle()

if __name__ == '__main__':
    encoder = OneHotEncoder()
    encoder.load_data()
    print(encoder.encode_sentence("Please turn on the light"))