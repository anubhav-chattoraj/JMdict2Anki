import xml.etree.ElementTree as etree

# doctype included in the JMDict XML file
# refer to it for details about the format

tree = etree.parse('~/JMdict_e')
root = tree.getroot();

