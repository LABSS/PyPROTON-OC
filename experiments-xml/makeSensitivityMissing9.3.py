import xml.etree.ElementTree as ET

repetitions = "10"

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
version="rp0.9.3"

for intervention in ['disruptive',
                     'preventive',
  'facilitators']:
    
        
    tree = ET.parse('rp_base.xml')
    root = tree.getroot()
    
    al = tree.find('.//enumeratedValueSet[@variable="intervention"]')
    for x in list(al): al.remove(x)
    al.insert(1, ET.Element("value", value='"'+intervention+'"'))        
            
    experiment = version + '_' + intervention + "_"  
    al = tree.find('.//experiment')
    al.set('name', version)
    al.set('repetitions', repetitions)        
    
    #write to file
    tree = ET.ElementTree(indent(root))
    tree.write(experiment + '.xml',  encoding='utf-8')


