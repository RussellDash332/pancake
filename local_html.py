# If you want to run from a local HTML file
from main import *
HTML_FN = 'run.html'

mode = get_mode()
while True:
    try:
        input(f'Paste the whole page source at {HTML_FN}, and press Enter when you\'re done:')
        with open(HTML_FN, 'rb') as f:
            html_doc = ''.join(map(bytes.decode, f.readlines()))
        parse(BeautifulSoup(html_doc, 'html.parser'))
        print()
    except KeyboardInterrupt: break
    except Exception as e:
        print('HTML page source cannot be parsed :( Skipping!')
        print('Issue:', e)