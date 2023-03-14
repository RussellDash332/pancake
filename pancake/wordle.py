from collections import Counter

class Wordle:
    def __init__(self, wordlist='data/wordle.txt'):
        self.wv, self.wordlist = [], wordlist

    def add(self, word, verdict):
        assert len(word) == len(verdict), 'Word and verdict must have the same length'
        assert not set(verdict.upper()) - {'G', 'Y', '-'}, 'Verdict must be combinations of G, Y, and -'
        self.wv.append([word.lower(), verdict.upper()])
        return self
    
    def solve(self):
        contains_yellow, contains_green, possible_frequencies = {}, {}, {}

        for word, verdict in self.wv:
            # temp stores the frequency of the green + yellow letters
            # e.g. SORRE GGYY- makes temp = {'s': 1, 'o': 1, 'r': 2}
            temp = {}
            for i in range(len(word)):
                if verdict[i] != '-':
                    if word[i] not in temp: temp[word[i]] = 0
                    temp[word[i]] += 1
            
            # update possible_frequencies dictionary such that
            # possible_frequencies[char] is the set of possible frequencies char can take
            for k in temp:
                if k not in possible_frequencies: possible_frequencies[k] = set(range(len(word)))
                possible_frequencies[k] -= set(range(temp[k]))
            for i in range(len(word)):
                if verdict[i] == '-':
                    if word[i] in temp: possible_frequencies[word[i]] = {temp[word[i]]}
                    else:               possible_frequencies[word[i]] = {0}

        # contains_yellow stores all possible indices of yellow characters
        for word, verdict in self.wv:
            for i in range(len(word)):
                if verdict[i] == 'Y':
                    if word[i] not in contains_yellow: contains_yellow[word[i]] = set(range(len(word)))
                    contains_yellow[word[i]] -= {i}

        # similarly for contains_green
        for word, verdict in self.wv:
            for i in range(len(word)):
                if verdict[i] == 'G':
                    if word[i] not in contains_green: contains_green[word[i]] = set()
                    contains_green[word[i]].add(i)

        # for neither yellow or green, we store all the possible letters
        illegal_letters = set()
        for word, verdict in self.wv:
            for i in range(len(word)):
                if verdict[i] == '-' and word[i] not in contains_yellow and word[i] not in contains_green:
                    illegal_letters.add(word[i])

        possible_words = set()
        for line in open(self.wordlist).readlines():
            word_to_check = line.strip()
            def do():
                # deep copy contains_green so we can perform elimination safely
                contains_green_copy = {}
                for k in contains_green:
                    contains_green_copy[k] = contains_green[k].copy()

                for i in range(len(word_to_check)):
                    if word_to_check[i] in illegal_letters:
                        return # cannot be a possible word
                    try:
                        # eliminate the letter if it's in contains_green_copy
                        contains_green_copy[word_to_check[i]].remove(i)
                        if not contains_green_copy[word_to_check[i]]: # key removal
                            del contains_green_copy[word_to_check[i]]
                    except:
                        # index is supposed to be at contains_yellow but it's not
                        # invalid word, can terminate early
                        if word_to_check[i] in contains_yellow and \
                            i not in contains_yellow[word_to_check[i]]:
                            return

                # Next checks that we can do: frequency matching
                word_cnt = Counter(word_to_check)
                for letter in word_cnt:
                    # frequency of letter is not possible for a valid word, terminate early
                    if letter in possible_frequencies and word_cnt[letter] not in possible_frequencies[letter]:
                        return
                for letter in possible_frequencies:
                    if letter in word_cnt:
                        # minimum of possible frequency exceeds what the word to check has, terminate early
                        if min(possible_frequencies[letter]) > word_cnt[letter]: return
                    elif min(possible_frequencies[letter]) > 0: # word_cnt[letter] is technically 0, terminate early as well
                        return

                # all green characters matched, so the dictionary should be empty now
                # passes all the yellow/neither letter checks as well
                if not contains_green_copy:
                    possible_words.add(word_to_check)
            do()
        return possible_words

if __name__ == '__main__':
    # Do a test run!
    w = Wordle()
    w.add('SOARE', 'G--Y-')
    w.add('STRIP', 'G-G--')
    w.add('SHRUB', 'G-GY-')

    for r in w.solve():
        print(r)

    input('\nPress enter to quit...')