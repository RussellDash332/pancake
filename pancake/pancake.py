from .wordle import Wordle
from collections import Counter, deque
from itertools import chain, combinations, product

def power_set(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

class Pancake:
    def __init__(self, size=5, swaps=10, wordlist='data/wordle.txt', board=None, verdict=None, name='pancake'):
        assert size % 2, 'Board size must be odd'
        self.size, self.swaps, self.wordlist, self.name = size, swaps, wordlist, name
        n = (size + 1) // 2
        # vertical
        vertical_indices = [[2*i] for i in range(n)]
        for _ in range(n-1):
            for i in range(n):
                vertical_indices[i].append(vertical_indices[i][-1] + size-i)
                vertical_indices[i].append(vertical_indices[i][-1] + n+i)
        self.vertical_indices = vertical_indices
        # horizontal
        offset = (3*size+1)//2
        self.horizontal_indices = [list(range(offset*i, offset*i+size)) for i in range(n)]
        # size**2 - ((size-1)//2)**2
        self.n_letters = (3*size-1)*(size+1)//4
        self.bv = None
        if board and verdict: self.supply(board, verdict)

    def supply(self, board, verdict):
        board = board.lower().strip()
        verdict = verdict.upper().strip()
        assert len(board) == len(verdict) == self.n_letters, f'Expecting {self.n_letters} characters from either board or verdict'
        self.bv = (board, verdict)

    def solve(self):
        def solve_single(wv):
            w, v = wv
            tmp = Wordle(self.wordlist).add(w, v).solve()
            yellow_intersections = [i for i in range(0, len(w), 2) if v[i] == 'Y']
            # List all possible changes yellow -> neither
            for to_change in power_set(yellow_intersections):
                if to_change:
                    new_v = list(v)
                    for i in to_change: new_v[i] = '-'
                    tmp |= Wordle(self.wordlist).add(w, ''.join(new_v)).solve()
            return tmp
        
        def make_actual_waffle(waffle, log=True):
            m = [['*']*self.size for _ in range(self.size)]
            waffle = waffle.upper()
            for i in range((self.size+1)//2):
                m[2*i] = waffle[self.size*i:self.size*(i+1)]
                for j in range((self.size-1)//2):
                    m[2*j+1][2*i] = waffle[self.size*(self.size+1)//2 + (self.size-1)//2*i + j]
            if log:
                print('-'*(2*self.size-1))
                for r in m: print(' '.join(r))
                print('-'*(2*self.size-1))
                print()
            return m
        
        def print_path(path, swaps_left=5):
            print(f'#{self.name} {swaps_left if swaps_left >= 0 else "X"}/5')
            
            print()
            m = [['⬜️' for _ in range(self.size)] for _ in range(self.size)]
            for i in range(self.size):
                for j in range(self.size):
                    if not (i % 2 and j % 2): m[i][j] = '🟩'
            mid = (self.size-1)//2
            pos = {
                1: [(mid, mid)],
                2: [(1, 1), (-2, -2)],
                3: [(1, 1), (mid, mid), (-2, -2)],
                4: [(1, 1), (1, -2), (-2, 1), (-2, -2)],
                5: [(1, 1), (1, -2), (-2, 1), (-2, -2), (mid, mid)]
            }
            for i, j in pos.get(swaps_left, []):
                m[i][j] = '⭐️'
            for r in m: print(''.join(r))

            print()
            print('🔥 streak: too many')
            print('🥇 #wafflegoldteam')
            print('wafflegame.net')

            print()
            m = [['  ' for _ in range(self.size)] for _ in range(self.size)]
            idx = 0
            for i in range(self.size):
                for j in range(self.size):
                    if not (i % 2 and j % 2):
                        m[i][j] = str(idx).zfill(2)
                        idx += 1
            print('```')
            for r in m:
                print(' '.join(r))
            print('```')

            print()
            print('Possible solution:')
            for i, (src, dest) in enumerate(path):
                print(f'{i+1}. Swap ||{str(src).zfill(2)}|| and ||{str(dest).zfill(2)}||')

        assert self.bv, 'Please supply board and verdict accordingly'
        waffle, verdicts = self.bv

        horizontal_words = [''.join(map(lambda x: waffle[x], indices)) for indices in self.horizontal_indices]
        horizontal_verdicts = [''.join(map(lambda x: verdicts[x], indices)) for indices in self.horizontal_indices]
        horizontal_solves = (list(map(solve_single, zip(horizontal_words, horizontal_verdicts))))

        vertical_words = [''.join(map(lambda x: waffle[x], indices)) for indices in self.vertical_indices]
        vertical_verdicts = [''.join(map(lambda x: verdicts[x], indices)) for indices in self.vertical_indices]
        vertical_solves = (list(map(solve_single, zip(vertical_words, vertical_verdicts))))

        # Check on intersections
        # Technically we only have to check some of them but for the sake of generality let's check all
        dim_intersection = (self.size+1)//2
        possible_intersect = [[[] for _ in range(dim_intersection)] for _ in range(dim_intersection)]
        for i in range(dim_intersection):
            for j in range(dim_intersection):
                for k in horizontal_solves[i]:
                    for l in vertical_solves[j]:
                        if k[2*j] == l[2*i]: possible_intersect[i][j].append((k, l))

        # Check for anagram
        waffle_ctr = Counter(waffle)

        # Intersection indices
        intersections = set()
        for i in range(dim_intersection):
            for j in range(dim_intersection):
                intersections |= set(self.horizontal_indices[i]) & set(self.vertical_indices[j])

        # List all possible words based on intersections
        possible_horizontal_words = [set() for _ in range(dim_intersection)]
        possible_vertical_words = [set() for _ in range(dim_intersection)]
        for i in range(dim_intersection):
            possible_horizontal_words[i] = {pair[0] for pair in possible_intersect[i][0]}
            possible_vertical_words[i] = {pair[1] for pair in possible_intersect[0][i]}
            for j in range(1, dim_intersection):
                possible_horizontal_words[i] &= {pair[0] for pair in possible_intersect[i][j]}
                possible_vertical_words[i] &= {pair[1] for pair in possible_intersect[j][i]}

        # Narrow down further
        for vertical_words in product(*possible_vertical_words):
            new_possible_horizontal_words = [set() for _ in range(dim_intersection)]
            for i in range(dim_intersection):
                for horizontal_word in possible_horizontal_words[i]:
                    if all([horizontal_word[2*j] == vertical_words[j][2*i] for j in range(dim_intersection)]):
                        new_possible_horizontal_words[i].add(horizontal_word)
            for horizontal_words in product(*new_possible_horizontal_words):
                new_waffle = ''.join(horizontal_words + tuple(map(lambda x: x[1::2], vertical_words)))

                # Found a possible anagram!
                if Counter(new_waffle) == waffle_ctr:
                    goal = make_actual_waffle(new_waffle, log=True) # print the goal state just in case
                    
                    # initiate stuff
                    target = sum([[a for a in b if a != '*'] for b in goal], start=[])
                    src = list(waffle.upper())

                    swaps_needed = self.swaps
                    greens = {i for i in range(self.n_letters) if src[i] == target[i]}
                    nongreens = set(range(self.n_letters)) - greens
                    starting_path = []

                    can_direct_swap = True
                    while can_direct_swap:
                        can_direct_swap = False
                        # Greedy: get two corrects at a time
                        for i in nongreens:
                            if not can_direct_swap:
                                for j in nongreens:
                                    if not can_direct_swap and i != j and \
                                    src[i] != target[i] and src[j] != target[j] and \
                                    src[i] == target[j] and src[j] == target[i]: # both same
                                        src[i], src[j] =  src[j], src[i]
                                        starting_path.append((i, j))
                                        swaps_needed -= 1
                                        can_direct_swap = True
                                        break
                        # Greedy(?): get one correct only if two cannot do
                        # TODO: check if there's a better strategy
                        if not can_direct_swap:
                            for i in nongreens:
                                if not can_direct_swap:
                                    for j in nongreens:
                                        if not can_direct_swap and i != j and \
                                        src[i] != target[i] and src[j] != target[j] and \
                                        (src[i] == target[j] or src[j] == target[i]): # either same
                                            src[i], src[j] =  src[j], src[i]
                                            starting_path.append((i, j))
                                            swaps_needed -= 1
                                            can_direct_swap = True
                                            break

                    if swaps_needed == 0:
                        print_path(starting_path)
                        continue
                    elif swaps_needed < 0:
                        print_path(starting_path, 5+swaps_needed)
                        print(f'Sub-optimal performance!{" (but it works...)" if swaps_needed >= -5 else ""}')
                        continue

                    # Worst case, if greedy doesn't work, do BFS
                    # But this is very very unlikely to be used
                    print('Greedy algorithm does not work, suggesting BFS...')
                    src, target, starting_path = ''.join(src), list(target), tuple(starting_path)
                    vis = {src}
                    q = deque([(list(src), 0, ())])
                    possible_paths = []
                    curr_level = 0
                    while q:
                        u, d, path = q.popleft()
                        if curr_level != d:
                            curr_level = d
                            print(f'Traversing {d}/{swaps_needed}, number of states: {len(q)}...')
                        if d == swaps_needed and u == target: possible_paths.append(starting_path+path)
                        else:
                            for i in nongreens:
                                for j in nongreens:
                                    if i != j and u[i] != target[i] and u[j] != target[j] and \
                                    (u[i] == target[j] or u[j] == target[i]):
                                        u[i], u[j] =  u[j], u[i]
                                        check = ''.join(u)
                                        if check not in vis:
                                            vis.add(check), q.append((u.copy(), d+1, path + ((i, j),)))
                                        u[i], u[j] =  u[j], u[i] # revert swap            
                    if len(possible_paths) > 1: print(f'Found {len(possible_paths)} possible paths! Showing a sample path...')
                    else: print()
                    print_path(possible_paths[0])

class DeluxePancake(Pancake):
    def __init__(self, board=None, verdict=None):
        super().__init__(size=7, swaps=20, wordlist='data/deluxe.txt', board=board, verdict=verdict, name='deluxepancake')

if __name__ == '__main__':
    # Do a test run
    Pancake(board='vahmrocisiapanlarlery', verdict='gyy-gyy-g-g-y---g-y-g').solve()
    DeluxePancake(board='riterrrotonthancuerwneicspineulelvrteepn', verdict='y-g-g-yy--ygyggg-g--y-g-gggygy-y--ygyg--').solve()
    input('\nPress enter to quit...')