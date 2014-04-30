import xml.etree.ElementTree as etree
import os.path

# the JMDict XML file contains a well-commented DTD
# refer to it for details about the format

# generator function that returns only common words that aren't all-kana
# change this to change the words which get included in the deck
def get_common_words(root):
  def is_common(priority_list):
    # utility function
    # takes a list of nodes (generated by findall) and returns whether the corresponding element is common
    common_priorities = {'news1', 'ichi1', 'spec1', 'gai1'} # words with one of these priorities are considered 'common'
    priority_list = [node.text for node in priority_list]
    priority_set = common_priorities.intersection(set(priority_list))
    return bool(priority_set)

  for entry in root:
    k_ele = entry.findall('k_ele')
    if not k_ele: continue # ignore all-kana words

    common = is_common(entry.findall('./ke_ele/ke_pri') + entry.findall('./r_ele/re_pri'))
    if not common: continue # ignore uncommon words

    # remove uncommon variants/readings
    for k_ele in entry.findall('k_ele'):
      if not is_common(k_ele.findall('ke_pri')): entry.remove(k_ele)
    for r_ele in entry.findall('r_ele'):
      if not is_common(r_ele.findall('re_pri')): entry.remove(r_ele)

    yield entry

# metaclass for the AnkiData class (which follows)
# This is just syntactic sugar; it makes 'word in AnkiData' work as expected
class MetaAnkiData(type):
  def __contains__(cls, word):
    return word in cls.notes_dict

# wrapper class for storing Anki notes without duplication
# we're going to store different words written with the same kanji as a single item
# because we're making a readings deck (not a vocab deck) and the card format is kanji → reading
class AnkiData(metaclass= MetaAnkiData):
  notes_dict = {} # format is 'headword': Note

  class Note:
    def __init__(self):
      self.readings = set()
      self.info = set() # info stores things like 'irregular okurigana usage' and 'ateji'

  @classmethod
  def add_word(cls, word):
    if word not in cls.notes_dict: cls.notes_dict[word] = cls.Note()

  @classmethod
  def add_reading(cls, word, reading):
    cls.add_word(word)
    cls.notes_dict[word].readings.add(reading)

  @classmethod
  def add_info(cls, word, info):
    cls.add_word(word)
    cls.notes_dict[word].info.add(info)

  @classmethod
  def write_to_csv(cls, csvfile):
    for word in cls.notes_dict:
      note = cls.notes_dict[word]
      reading = '<br/>'.join(note.readings)
      info = ';'.join(note.info)
      csvfile.write('\t'.join([word, reading, info]) + '\n')

# takes an entry node and converts it into one or more csv lines
# change this if you want to change the structure of the Anki deck
def process_word(entry):
  entry_words = [] # for storing the words whose readings are given in the <r_ele> nodes

  for keb in entry.findall('./k_ele/keb'):
    word = keb.text
    ke_inf = entry.findall('./k_ele/ke_inf')
    for node in ke_inf:
      AnkiData.add_info(word, node.text)
    entry_words.append(word)

  for r_ele in entry.findall('r_ele'):
    if r_ele.findall('re_nokanji'): continue # this r_ele is not a reading of the word

    reading = r_ele.find('reb').text
    words = [node.text for node in r_ele.findall('re_restr')]
    if words: # this reading is restricted to particular words in the entry
      for word in words:
        if word in AnkiData: AnkiData.add_reading(word, reading)
    else: # reading applies to all words in the entry
      for word in entry_words: AnkiData.add_reading(word, reading)

  # If one needs to extract the meanings of the words, this is where the code for that would go
  # The meanings are stored under the <sense> children of <entry>
  # A <sense> can be restricted to a particular word/reading, depending on its <stagk> and <stagr> children
  # To handle these properly, one would need to use more elaborate data structures than the two dictionaries I used
  # Coding this is left as an exercise to whoever actually needs that data

homedir = os.path.expanduser('~')
jmdict = os.path.join(homedir, 'JMdict_e') # change the path to point to the JMdict file
tree = etree.parse(jmdict)
root = tree.getroot()
word_generator = get_common_words(root)

for word in word_generator: process_word(word)

# write words to CSV file
csvfile = open(os.path.join(homedir, 'words.csv'), 'w', encoding = 'utf-8')
AnkiData.write_to_csv(csvfile)
csvfile.close()
