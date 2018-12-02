import pickle
from pathlib import Path

class FileHandler:
    # input file containing the training corpus
    input_training_corpus = "persistent/trainingCorpus.txt"
    # file containing the stemmed training corpus
    refined_training_corpus = "persistent/refinedTrainingCorpus.txt"
    # contains the used lexicon
    lexicon_pickle_file = 'persistent/lexicon.pickle'
    # contains the encoded (final) training corpus
    training_pickle_file = "persistent/training_corpus.pickle"
    # contains all the encoded vocabulary data
    vocabulary_data_pickle_file = "persistent/vocabulary_data.pickle"

    def __init__(self):
        pass

    def read_training_corpus(self):
        """
        Reads the entire content of the file containing the initial training corpus

        :return: List containing all the lines of the file
        """
        return self.read_all_from_file(self.input_training_corpus)

    def write_refined_training_corpus(self, data):
        """
        Writes the list of refined training corpus to file

        :param data: the refined training corpus
        :return: None
        """
        self.write_list_to_file(self.refined_training_corpus, data)

    def read_refined_training_corpus(self):
        """
        Reads the entire content of the file containing the refined training corpus

        :return: List containing all the lines of the file
        """
        return self.read_all_from_file(self.refined_training_corpus)

    def write_training_pickle(self, data):
        """
        Writes the input content into the training pickle file

        :param data: The data to be written into the pickle file
        :return: None
        """
        self.write_to_pickle(self.training_pickle_file, data)

    def write_lexicon_pickle(self, data):
        """
        Writes the input content into the lexicon pickle file

        :param data: The data to be written into the pickle file
        :return: None
        """
        self.write_to_pickle(self.lexicon_pickle_file, data)

    def read_lexicon_pickle(self):
        """
        Returns the content of the lexicon pickle file

        :return: The content
        """
        return self.load_from_pickle(self.lexicon_pickle_file)

    def write_vocabulary_data_pickle(self, data):
        """
        Writes the input content into the vocabulary data pickle file

        :param data: The data to be written into the pickle file
        :return: None
        """
        self.write_to_pickle(self.vocabulary_data_pickle_file, data)

    def read_vocabulary_data_pickle(self):
        """
        Returns the content of the vocabulary data pickle file
        :return: The content
        """
        return self.load_from_pickle(self.vocabulary_data_pickle_file)

    def vocabulary_data_pickle_exists(self):
        """
        Checks whether the vocabulary data pickle file exists

        :return: True - the file exists
                 False - otherwise
        """
        return self.file_exists(self.vocabulary_data_pickle_file)

    def load_from_pickle(self, pickle_path):
        """
        Deserializes the pickle file specified by pickle_path and returns its content

        :param pickle_path: The path to the pickle file to read
        :return: The deserialized content of the pickle file
        """
        with open(pickle_path, 'rb') as file:
            return_data = pickle.load(file)
            file.close()
        return return_data

    def write_to_pickle(self, pickle_path, data):
        """
        Writes the content of tha data input, to a pickle specified by pickle_path

        :param pickle_path: the path to the output pickle
        :param data: the data to pe persisted in the pickle
        :return: None
        """
        with open(pickle_path, 'wb') as file:
            pickle.dump(data, file)
            file.flush()
            file.close()

    def read_all_from_file(self, file_path):
        """
        Reads the content of the input file and returns said content as a list of lines

        :param file_path: the path to the file to read
        :return: List of all the lines read from the file
        """
        with open(file_path, 'r') as file:
            lines = file.readlines()
        return lines

    def write_list_to_file(self, file_path, data_list):
        """
        Writes the content of the data_list, line by line, into the file_path

        :param file_path: the output file
        :param data_list: the list to be written to file
        :return: None
        """
        with open(file_path, 'w') as file:
            for entry in data_list:
                file.write("%s\n" % entry)
            file.flush()
            file.close()

    def file_exists(self, file_path):
        """
        Checks whether a file exists

        :param file_path: the file to check
        :return: True - the file exists
                 False - otherwise
        """
        file = Path(file_path)
        if file.is_file():
            return True
        return False
