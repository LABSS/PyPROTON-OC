import xml.etree.ElementTree as ET

repetitions = 20

#pretty print method
def indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem

# ----------------------------------
version="rp0.61p"
tree = ET.parse('rp_base.xml')
root = tree.getroot()

al = tree.find('.//experiment')
print(al)
al.set('name', version)
al.set('repetitions', str(int(repetitions/3)))

al = tree.find('.//enumeratedValueSet[@variable="intervention"]')
for x in al.getchildren(): al.remove(x)
al.insert(1, ET.Element("value", value='"preventive"'))
al.insert(1, ET.Element("value", value='"students"'))
al.insert(1, ET.Element("value", value='"facilitators"'))

al = tree.find('.//enumeratedValueSet[@variable="num-persons"]')
for x in al.getchildren(): al.remove(x)
al.insert(1, ET.Element("value", value="3000"))

#write to file
tree = ET.ElementTree(indent(root))
tree.write(version + '.xml',  encoding='utf-8')




