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

# takes an entry node and converts it into one or more csv lines
# change this if you want to change the structure of the Anki deck
def process_word(entry):
  # readings is { word: [reading] }, info is {word: 'information'}
  # where information is usually 'Irregular okurigana usage'
  readings = {}
  info = {}

  for keb in entry.findall('./k_ele/keb'):
    readings[keb.text] = [];
    ke_inf = entry.findall('./k_ele/ke_inf')
    if ke_inf:
      info[keb.text] = ','.join(node.text for node in ke_inf)
    else:
      info[keb.text] = ''

  for r_ele in entry.findall('r_ele'):
    if r_ele.findall('re_nokanji'): continue # this r_ele is not a reading of the word

    reading = r_ele.find('reb').text
    words = [node.text for node in r_ele.findall('re_restr')]
    if words: # this reading is restricted to particular words in the entry
      for word in words:
        if word in readings: readings[word].append(reading)
    else: # reading applies to all words in the entry
      for word in readings: readings[word].append(reading)

  # If one needs to extract the meanings of the words, this is where the code for that would go
  # The meanings are stored under the <sense> children of <entry>
  # A <sense> can be restricted to a particular word/reading, depending on its <stagk> and <stagr> children
  # To handle these properly, one would need to use more elaborate data structures than the two dictionaries I used
  # Coding this is left as an exercise to whoever actually needs that data

  # output each word as a line of the csv file (corresponds to a single Anki note)
  for word in readings:
    csv_line = '\t'.join([word, '<br/>'.join(readings[word]), info[word]])
    print(csv_line)

path = os.path.join(os.path.expanduser('~'), 'JMdict_e') # change the path to point to the JMdict file
tree = etree.parse(path)
root = tree.getroot();
word_generator = get_common_words(root)

for word in word_generator:
  process_word(word)
