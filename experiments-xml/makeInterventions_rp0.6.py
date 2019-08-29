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
version="rp0.6p"
tree = ET.parse('rp_base.xml')
root = tree.getroot()


al = tree.find('.//experiment')
print(al)
al.set('name', version)
al.set('repetitions', str(int(repetitions/3)))

al = tree.find('.//enumeratedValueSet[@variable="intervention"]')
al.insert(1, ET.Element("value", value='"disruptive"'))
al.insert(1, ET.Element("value", value='"students"'))
al.insert(1, ET.Element("value", value='"facilitators"'))

al = tree.find('.//enumeratedValueSet[@variable="data-folder"]')

al = tree.find('.//enumeratedValueSet[@variable="num-persons"]')
for x in al.getchildren(): al.remove(x)
al.insert(1, ET.Element("value", value="3000"))


#write to file
tree = ET.ElementTree(indent(root))
tree.write(version + '.xml',  encoding='utf-8')


# ----------------------------------
version="rp0.6e"
tree = ET.parse('rp_base.xml')
root = tree.getroot()


al = tree.find('.//experiment')
al.set('name', version)
al.set('repetitions', str(int(repetitions/3)))

al = tree.find('.//enumeratedValueSet[@variable="intervention"]')
al.insert(1, ET.Element("value", value='"preventive"'))
al.insert(1, ET.Element("value", value='"disruptive"'))
al.insert(1, ET.Element("value", value='"students"'))
al.insert(1, ET.Element("value", value='"facilitators"'))

al = tree.find('.//enumeratedValueSet[@variable="data-folder"]')
for x in al.getchildren(): al.remove(x)
al.insert(1, ET.Element("value", value='"inputs/eindhoven/data/"'))

al = tree.find('.//enumeratedValueSet[@variable="num-persons"]')
for x in al.getchildren(): al.remove(x)
al.insert(1, ET.Element("value", value="3000"))

# the three eindhoven basic changes
al = tree.find('.//enumeratedValueSet[@variable="num-oc-persons"]')
for x in al.getchildren(): al.remove(x)
al.insert(1, ET.Element("value", value="15"))
al = tree.find('.//enumeratedValueSet[@variable="number-crimes-yearly-per10k"]')
for x in al.getchildren(): al.remove(x)
al.insert(1, ET.Element("value", value="3368"))
al = tree.find('.//enumeratedValueSet[@variable="number-arrests-per-year"]')
for x in al.getchildren(): al.remove(x)
al.insert(1, ET.Element("value", value="15"))
al = tree.find('.//enumeratedValueSet[@variable="num-oc-families"]')
for x in al.getchildren(): al.remove(x)
al.insert(1, ET.Element("value", value="4"))


#write to file
tree = ET.ElementTree(indent(root))
tree.write(version + '.xml',  encoding='utf-8')




