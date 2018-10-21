# https://www.youtube.com/watch?v=7fcWfUavO7E&index=48&list=PLQVvvaa0QuDfKTOs3Keq_kaG2P55YRn5v

import pickle
import random
from collections import Counter

import numpy as np
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

lemmatizer = WordNetLemmatizer()
hm_lines = 10000000

# https://www.youtube.com/watch?v=YFxVHD2TNII&index=49&list=PLQVvvaa0QuDfKTOs3Keq_kaG2P55YRn5v

def create_lexicon(pos, neg):
    # create a lexicon with all the words from the input files
    lexicon = []
    for file in [pos, neg]:
        with open(file, 'r') as f:
            contents = f.readlines()
            for l in contents[:hm_lines]:
                all_words = word_tokenize(l.lower())
                lexicon += list(all_words)
    # lemmatize everything
    lexicon = [lemmatizer.lemmatize(i) for i in lexicon]
    w_counts = Counter(lexicon)

    final_lexicon = []
    # filter out words that are way too often and way too seldom
    for w in w_counts:
        if 1000 > w_counts[w] > 50:
            final_lexicon.append(w)

    print("lexicon size", len(final_lexicon))
    print("lexicon", final_lexicon)
    return final_lexicon

def sample_handling(sample, lexicon, classification):
    feature_set = []

    with open(sample, 'r') as f:
        contents = f.readlines()
        for l in contents[:hm_lines]:
            current_words = word_tokenize(l.lower())
            current_words = [lemmatizer.lemmatize(i) for i in current_words]
            features = np.zeros(len(lexicon))
            for word in current_words:
                if word.lower() in lexicon:
                    index_value = lexicon.index(word.lower())
                    features[index_value] += 1

            features = list(features)
            feature_set.append([features, classification])

    return feature_set

def create_feature_sets_and_labels(pos, neg, test_size=0.1):
    lexicon = create_lexicon(pos, neg)
    features = []
    features += sample_handling(pos, lexicon, [1, 0])
    features += sample_handling(neg, lexicon, [0, 1])
    random.shuffle(features)

    features = np.array(features)

    testing_size = int(test_size * len(features))

    train_x = list(features[:,0][:-testing_size])
    train_y = list(features[:,1][:-testing_size])

    test_x = list(features[:,0][-testing_size:])
    test_y = list(features[:,1][-testing_size:])

    return train_x, train_y, test_x, test_y

if __name__ == '__main__':

    train_x, train_y, test_x, test_y = create_feature_sets_and_labels('textData/pos.txt', 'textData/neg.txt')
    with open('sentiment_set.pickle', 'wb') as f:
        pickle.dump([train_x, train_y, test_x, test_y], f)
        f.close()

"""
    This took the content of both pos.txt and neg.txt files containing positive and negative reviews and 
    created 423 lexicon entries.
    After processing, it created a pickle file of 139.9 MB
"""