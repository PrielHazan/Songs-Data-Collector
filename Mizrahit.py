from bs4 import BeautifulSoup
import requests
import csv

def Hebrew_Multi_Lines(paper):
    digits = []
    new_paper = []
    for line in iter(paper.splitlines()):
        for char in line[::-1]:
            if char.isdigit():
                digits.insert(0, char)
                continue
            #if list is empty
            if not(digits):
                new_paper.append(char)
            else:
                new_paper.append(str(''.join(digits)))
                new_paper.append(char)
                digits.clear()
        new_paper.append('\n')
    new_paper = ''.join(new_paper)
    return new_paper

Hebrew_Letters = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת']


def extract_songs_names(string):
    songs_names = []
    for line in iter(string.splitlines()):
        if len(line) < 2:
            continue
        else:
            song_name = line.split('-')
            if '(' in song_name[0]:
                song_real_name = song_name[0].split('(')[1]
            else:
                song_real_name = song_name[0]
            songs_names.append(song_real_name.strip())
    return songs_names

def print_Indexed_list(list_):
    for idx, item in enumerate(list_):
        print('index of item is', idx)
        print(Hebrew_Multi_Lines(item.get_text()))


def add_Song_To_CSV(url, singer, song_name):
    try:
        source1 = requests.get(url).text

        soup = BeautifulSoup(source1, 'lxml')

        spans = soup.findAll('span')
        divs = soup.findAll('div')
        spans_index = 0
        if len(spans[5].get_text()) < 2:
            spans_index = 1

        date = spans[7+spans_index].get_text()[-8:]
        text = divs[13].get_text()
        poet = spans[5+spans_index].get_text()
        # melody = spans[6+spans_index].get_text()

        csv_writer.writerow([singer, song_name[::-1], date, text.strip(), poet])

    except:
        print('song writing to csv failed')






def add_Singer_Songs_To_CSV(singer_page_url):
    global song_index
    source2 = requests.get(singer_page_url).text
    soup = BeautifulSoup(source2, 'lxml')
    spans = soup.findAll('span')
    divs = soup.findAll('div')
    tds = soup.findAll('td')
    songs_names = extract_songs_names(tds[25].get_text()[::-1])
    singer = tds[24].get_text()[17:]
    a_td = tds[23]
    a_elems = a_td.findAll('a')
    urls = ['http://www.mizrahit.co/' + a_elem['href'] for a_elem in a_elems if 'id' in a_elem['href']]
    for idx, url in enumerate(urls):
        try:
            add_Song_To_CSV(url, singer, songs_names[idx])
            print(f'song number {song_index} name: {songs_names[idx]} added to csv')
        except:
            print(f'song number {song_index} name: {songs_names[idx]} was not added to csv')
        finally:
            song_index += 1

def add_Songs_By_Starting_Letter(letter):
    try:
        source3 = requests.get(f'http://www.mizrahit.co/lyrics.php?leng={letter}').text
        soup = BeautifulSoup(source3, 'lxml')
        tds = soup.findAll('td')
        a_td = tds[23]
        a_s = a_td.findAll('a')[2:]
        hrefs = ['http://www.mizrahit.co/' + a['href'] for a in a_s]
        for idx, href in enumerate(hrefs):
            add_Singer_Songs_To_CSV(href)
            print('Singer indexed: ', idx, 'of the letter: ', letter, 'completed')

    except:
        print('Singer indexed: ', idx, 'of the letter: ', letter, 'raised an error')


song_index = 0

csv_file = open('Mizrahit.csv', 'w')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['singer', 'song name', 'date', 'text', 'poet'])
for letter in Hebrew_Letters:
    try:
        add_Songs_By_Starting_Letter(letter)
        print('Done with letter: ', letter)
    except:
        print('error occured with letter: ', letter)

csv_file.close()

