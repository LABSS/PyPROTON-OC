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
version="rp0.9.2"

variations={'number-crimes-yearly-per10k': [1000, 3000],
 'unemployment-multiplier': [1.5, 0.5],
 'number-arrests-per-year': [15, 45],
 'punishment-length': [1.5, 0.5]
 }

for intervention in ['disruptive',
  'students',
  'baseline',
  'preventive',
  'facilitators']:
    
# this goes by itself as it has a double set to do    
    for nocc in [[15,6], [45,8]]:
        tree = ET.parse('rp_base.xml')
        root = tree.getroot()
        
        al = tree.find('.//enumeratedValueSet[@variable="intervention"]')
        for x in list(al): al.remove(x)
        al.insert(1, ET.Element("value", value='"'+intervention+'"'))        
        
        al = tree.find('.//enumeratedValueSet[@variable="num-oc-persons"]')
        for x in list(al): al.remove(x)
        al.insert(1, ET.Element("value", value=str(nocc[0])))
        al = tree.find('.//enumeratedValueSet[@variable="num-oc-families"]')
        for x in list(al): al.remove(x)
        al.insert(1, ET.Element("value", value=str(nocc[1])))
        
        experiment = version + '_' + intervention + '_NOC_' + str(nocc[0]) 
        al = tree.find('.//experiment')
        al.set('name', version)
        al.set('repetitions', repetitions)        

        #write to file
        tree = ET.ElementTree(indent(root))
        tree.write(experiment + '.xml',  encoding='utf-8')
        
        for var in variations:
                for v in variations.get(var):
                    tree = ET.parse('rp_base.xml')
                    root = tree.getroot()
                    
                    al = tree.find('.//enumeratedValueSet[@variable="intervention"]')
                    for x in list(al): al.remove(x)
                    al.insert(1, ET.Element("value", value='"'+intervention+'"'))        
                    
                    al = tree.find('.//enumeratedValueSet[@variable="' + var + '"]')
                    for x in list(al): al.remove(x)
                    al.insert(1, ET.Element("value", value=str(v)))
        
                    experiment = version + '_' + intervention + "_" + var + "_" + str(v) 
                    al = tree.find('.//experiment')
                    al.set('name', version)
                    al.set('repetitions', repetitions)        

                    #write to file
                    tree = ET.ElementTree(indent(root))
                    tree.write(experiment + '.xml',  encoding='utf-8')


