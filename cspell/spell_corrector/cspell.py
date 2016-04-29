

# spell checking and correction module
import re
import time
import csv
# import sys
import ast


class cspell:
    max_edit_distance = 3
    verbose = 0
    # 0: top suggestion
    # 1: all suggestions of smallest edit distance
    # 2: all suggestions <= max_edit_distance (slower,  no early termination)
    dictionary = {}
    longest_word_length = 0

    def __init__(self, dictfile):
        start_time = time.time()
        cache_dict = "cache_dict.csv"
        try:
            w = csv.reader(open(cache_dict, "r"))
            for row in w:
                [key,  value] = row
                self.longest_word_length = max(self.longest_word_length,
                        len(key))
                self.dictionary[key] = ast.literal_eval(value)
        except FileNotFoundError:
                self.create_dictionary(dictfile)
                w = csv.writer(open(cache_dict, "w"))
                for key,  val in self.dictionary.items():
                    w.writerow([key,  val])
        # wc = open(dictfile,"r")
        # for line in wc:
            # line = line.rstrip('\n')
            # line = line.replace("\t", " ")
            # word = line.split(" ")
            # self.longest_word_length = max(self.longest_word_length, len(word[0]))
            # self.dictionary[word[0]] = [ [], int(word[1])]
        run_time = time.time() - start_time
        print('-----')
        print('%.2f seconds to run' % run_time)
        print('-----')

    def get_deletes_list(self, w):
        '''given a word,  derive strings with up to max_edit_distance characters
        deleted'''
        deletes = []
        queue = [w]
        for d in range(self.max_edit_distance):
            temp_queue = []
            for word in queue:
                if len(word) > 1:
                    for c in range(len(word)):  # character index
                        word_minus_c = word[:c] + word[c+1:]
                        if word_minus_c not in deletes:
                            deletes.append(word_minus_c)
                            if word_minus_c not in temp_queue:
                                temp_queue.append(word_minus_c)
                                queue = temp_queue

        return deletes

    def create_dictionary_entry(self, w):
        '''add word and its derived deletions to dictionary'''
        # check if word is already in dictionary
        # dictionary entries are in the form: (list of suggested corrections,
        # frequency of word in corpus)
        new_real_word_added = False
        if w in self.dictionary:
            # increment count of word in corpus
            self.dictionary[w] = (self.dictionary[w][0],
                                  self.dictionary[w][1] + 1)
        else:
            self.dictionary[w] = ([],  1)
            self.longest_word_length = max(self.longest_word_length,  len(w))

        if self.dictionary[w][1] == 1:
            # first appearance of word in corpus
            # n.b. word may already be in dictionary as a derived word
            # (deleting character from a real word)
            # but counter of frequency of word in corpus is not incremented
            # in those cases)
            new_real_word_added = True
            deletes = self.get_deletes_list(w)
            for item in deletes:
                if item in self.dictionary:
                    # add (correct) word to delete's suggested correction list
                    # if not already there
                    if item not in self.dictionary[item][0]:
                        self.dictionary[item][0].append(w)
                    else:
                        # note frequency of word in corpus is not incremented
                        self.dictionary[item] = ([w],  0)

        return new_real_word_added

    def create_dictionary(self, fname):

        total_word_count = 0
        unique_word_count = 0

        with open(fname) as file:
            print("Creating dictionary...")
            for line in file:
                # separate by words by non-alphabetical characters
                words = re.findall('[a-z]+',  line.lower())
                for word in words:
                    total_word_count += 1
                    if self.create_dictionary_entry(word):
                        unique_word_count += 1

        print("total words processed: %i" % total_word_count)
        print("total unique words in corpus: %i" % unique_word_count)
        print("total items in dictionary(corpus words and deletions): %i"
              % len(self.dictionary))
        print("edit distance for deletions: %i" % self.max_edit_distance)
        print("length of longest word in corpus: %i"
              % self.longest_word_length)

        return self.dictionary

    def dameraulevenshtein(self, s1, s2):
        d = {}
        lenstr1 = len(s1)
        lenstr2 = len(s2)
        for i in range(-1, lenstr1+1):
            d[(i, -1)] = i+1
        for j in range(-1, lenstr2+1):
            d[(-1, j)] = j+1
        for i in range(lenstr1):
            for j in range(lenstr2):
                if s1[i] == s2[j]:
                    cost = 0
                else:
                    cost = 1
                d[(i, j)] = min(d[(i-1, j)] + 1,  # deletion
                                d[(i, j-1)] + 1,  # insertion
                                d[(i-1, j-1)] + cost,  # substitution
                                )
                if i and j and s1[i] == s2[j-1] and s1[i-1] == s2[j]:
                    d[(i, j)] = min(d[(i, j)],
                                    d[i-2, j-2] + cost)  # transposition

        return d[lenstr1-1, lenstr2-1]

    def get_suggestions(self, string, silent=False):
        '''return list of suggested corrections for potentially incorrectly
        spelled word'''
        if (len(string) - self.longest_word_length) > self.max_edit_distance:
            if not silent:
                print("no items in dictionary within maximum edit distance")
                return []

        suggest_dict = {}
        min_suggest_len = float('inf')

        queue = [string]
        q_dictionary = {}  # items other than string that we've checked

        splits = [(string[:i], string[i:]) for i in range(len(string) + 1)]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
        for transpose in transposes:
            if transpose not in q_dictionary:
                queue.append(transpose)
                q_dictionary[transpose] = None
                # arbitrary value,  just to identify we checked this

        while len(queue) > 0:
            q_item = queue[0]  # pop
            queue = queue[1:]

            # early exit
            if ((self.verbose < 2) and (len(suggest_dict) > 0) and
               ((len(string) - len(q_item)) > min_suggest_len)):
                break

            # process queue item
            if (q_item in self.dictionary) and (q_item not in suggest_dict):
                if (self.dictionary[q_item][1] > 0):
                    # word is in dictionary, & is a word from the corpus, &
                    # not already in suggestion list so add to suggestion
                    # dictionary,  indexed by the word with value (frequency in
                    # corpus,  edit distance)
                    # note q_items that are not the input string are shorter
                    # than input string since only deletes are added (unless
                    # manual dictionary corrections are added)
                    assert len(string) >= len(q_item)
                    suggest_dict[q_item] = (self.dictionary[q_item][1],
                                            len(string) - len(q_item))
                    # early exit
                    if ((self.verbose < 2) and (len(string) == len(q_item))):
                        break
                    elif (len(string) - len(q_item)) < min_suggest_len:
                        min_suggest_len = len(string) - len(q_item)

                # the suggested corrections for q_item as stored in
                # dictionary (whether or not q_item itself is a valid word
                # or merely a delete) can be valid corrections
                for sc_item in self.dictionary[q_item][0]:
                    if (sc_item not in suggest_dict):

                        # compute edit distance
                        # suggested items should always be longer
                        # (unless manual corrections are added)
                        assert len(sc_item) > len(q_item)

                        # q_items that are not input should be shorter
                        # than original string
                        # (unless manual corrections added)
                        assert len(q_item) <= len(string)

                        if len(q_item) == len(string):
                            assert q_item == string
                            item_dist = len(sc_item) - len(q_item)

                        # item in suggestions list should not be the same as
                        # the string itself
                        assert sc_item != string

                        # calculate edit distance using,  for example,
                        # Damerau-Levenshtein distance
                        item_dist = self.dameraulevenshtein(sc_item,  string)

                        # do not add words with greater edit distance if
                        # verbose setting not on
                        if ((self.verbose < 2) and
                           (item_dist > min_suggest_len)):
                            pass
                        elif item_dist <= self.max_edit_distance:
                            assert sc_item in self.dictionary  # should already be in dictionary if in suggestion list
                            suggest_dict[sc_item] = (
                                self.dictionary[sc_item][1], item_dist)
                            if item_dist < min_suggest_len:
                                min_suggest_len = item_dist

                        # depending on order words are processed,  some words
                        # with different edit distances may be entered into
                        # suggestions; trim suggestion dictionary if verbose
                        # setting not on
                        if self.verbose < 2:
                            suggest_dict = {
                                k: v for k,  v in suggest_dict.items()
                                if v[1] <= min_suggest_len}

            # now generate deletes (e.g. a substring of string or of a delete)
            # from the queue item
            # as additional items to check -- add to end of queue
            assert len(string) >= len(q_item)

            # do not add words with greater edit distance if verbose setting
            # is not on
            if ((self.verbose < 2) and
               ((len(string) - len(q_item)) > min_suggest_len)):
                pass
            elif (len(string) - len(q_item)) < self.max_edit_distance and len(q_item) > 1:
                for c in range(len(q_item)):  # character index
                    word_minus_c = q_item[:c] + q_item[c+1:]
                    if word_minus_c not in q_dictionary:
                        queue.append(word_minus_c)
                        q_dictionary[word_minus_c] = None  # arbitrary value,  just to identify we checked this

        # queue is now empty: convert suggestions in dictionary to
        # list for output
        if not silent and self.verbose != 0:
            print("number of possible corrections: %i" % len(suggest_dict))
            print("  edit distance for deletions: %i" % self.max_edit_distance)

        # output option 1
        # sort results by ascending order of edit distance and descending
        # order of frequency
        #     and return list of suggested word corrections only:
        # return sorted(suggest_dict,  key = lambda x:
        #               (suggest_dict[x][1],  -suggest_dict[x][0]))

        # output option 2
        # return list of suggestions with (correction,
        #                                  (frequency in corpus,  edit distance)):
        as_list = suggest_dict.items()
        outlist = sorted(as_list,  key=lambda term_f_d: (term_f_d[1][1], -term_f_d[1][0]))

        if self.verbose == 0:
            if len(outlist) > 0:
                return outlist[0]
            return None
        else:
            return outlist

        '''
        Option 1:
            ['file',  'five', 'fire', 'fine', ...]

        Option 2:
            [('file',  (5, 0)),
            ('five',  (67, 1)),
            ('fire',  (54, 1)),
            ('fine',  (17, 1))...]
            '''

    def best_word(self, s, silent=False):
        try:
            return self.get_suggestions(s,  silent)[0]
        except:
            return None

    def correct_document(self, fname, printlist=True):
        # correct an entire document
        with open(fname) as file:
            doc_word_count = 0
            corrected_word_count = 0
            unknown_word_count = 0
            print("Finding misspelled words in your document...")

            for i,  line in enumerate(file):
                # separate by words by non-alphabetical characters
                doc_words = re.findall('[a-z]+',  line.lower())
                for doc_word in doc_words:
                    doc_word_count += 1
                    suggestion = self.best_word(doc_word,  silent=True)
                    if suggestion is None:
                        if printlist:
                            print("In line %i,  the word < %s > was not found (no suggested correction)" % (i, doc_word))
                            unknown_word_count += 1
                        elif suggestion[0]!=doc_word:
                            if printlist:
                                print("In line %i,  %s: suggested correction is < %s >" % (i, doc_word, suggestion[0]))
                                corrected_word_count += 1

        print("-----")
        print("total words checked: %i" % doc_word_count)
        print("total unknown words: %i" % unknown_word_count)
        print("total potential errors found: %i" % corrected_word_count)

        return

    def check(self, word):
        start_time = time.time()
        if word in self.dictionary:
            sugg = True
        else:
            sugg = self.get_suggestions(word)
            sugg = sugg[0]
        run_time = time.time() - start_time
        print('%.5f seconds to run' % run_time)
        return sugg


if __name__ == "__main__":

    dictfile = "../files/big.txt"
    cp = cspell(dictfile)

    print("Word correction ")
    print("---------------")

    while True:
        word_in = input('Enter your input (or enter to exit): ')
        if len(word_in) == 0:
            print("exiting.......")
            break
        start_time = time.time()
        print(cp.get_suggestions(word_in))  # or use the check function
        run_time = time.time() - start_time
        print('-----')
        print('%.5f seconds to run' % run_time)
        print('-----')
        print(" ")
