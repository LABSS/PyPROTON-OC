import xml.etree.ElementTree as ET
import prettyprint

repetitions = 3

version="rp0.7e"

ocfamilies = {'8':'3', '15':'6',  '30':'8'}

for ocmembers in ['8', '15', '30']:
    for employmentrate in ['0.205033763044813', '0.410067526089626', '0.615101289134438']:
        for intervention in ['"baseline"','"preventive"', '"disruptive"', '"students"','"facilitators"']:

            tree = ET.parse('rp0.7e_base.xml')
            root = tree.getroot()

            al = tree.find('.//experiment')
            al.set('repetitions', str(3))

            experiment = "_".join([version, ocmembers, employmentrate[2:4], intervention.replace('"', '')])
            al = tree.find('.//experiment')
            al.set('name', experiment)
            al = tree.find('.//enumeratedValueSet[@variable="num-oc-persons"]')
            al.insert(1, ET.Element("value", value=ocmembers))
            al = tree.find('.//enumeratedValueSet[@variable="num-oc-families"]')
            al.insert(1, ET.Element("value", value=ocfamilies.get(ocmembers)))


            al = tree.find('.//enumeratedValueSet[@variable="intervention"]')
            al.insert(1, ET.Element("value", value=intervention))


            al = tree.find('.//enumeratedValueSet[@variable="unemployment-multiplier"]')
            al.insert(1, ET.Element("value", value=employmentrate))


            #write to file
            tree = ET.ElementTree(prettyprint.indent(root))
            tree.write(experiment + '.xml',  encoding='utf-8')




