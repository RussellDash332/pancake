import requests

fn, length = '../data/deluxe.txt', 7
print(fn, length)
input('Press enter to continue...') 

words = [word.strip() for word in open(fn).readlines()]
new_words = []
page = 1
while True:
    r = requests.get('https://fly.wordfinderapi.com/api/search',
                    params={
                        'length':length,
                        'page_token':page,
                        'page_size':10000,
                        'word_sorting':'az',
                        'group_by_length':False,
                        'dictionary':'all_en'
                    })
    rjson = r.json()
    new_words.extend(t['word'] for t in rjson['word_pages'][0]['word_list'])
    if rjson['word_pages'][0]['num_pages'] == page: break
    page += 1

print(len(words), len(new_words))
final_words = sorted(filter(lambda x: len(x) == length, set(words) | set(new_words)))
print(len(final_words))
with open(fn, 'w+') as f:
    f.write('\n'.join(final_words))