#/bin/bash
awk '/<enumeratedValueSet variable=\"employment-rate\">/,/ <\/enumeratedValueSet>/ {sub(/value=\"1\"/,"value=\"1\.5\"")}1' exp-OC-baseEduEco.xml > exp-OC-highEduEco2.xml
awk '/<enumeratedValueSet variable=\"education-rate\">/,/ <\/enumeratedValueSet>/ {sub(/value=\"1\"/,"value=\"1\.5\"")}1' exp-OC-highEduEco2.xml > exp-OC-highEduEco.xml
rm exp-OC-highEduEco2.xml
awk '/<enumeratedValueSet variable=\"employment-rate\">/,/ <\/enumeratedValueSet>/ {sub(/value=\"1\"/,"value=\"0\.5\"")}1' exp-OC-baseEduEco.xml > exp-OC-lowEduEco2.xml
awk '/<enumeratedValueSet variable=\"education-rate\">/,/ <\/enumeratedValueSet>/ {sub(/value=\"1\"/,"value=\"0\.5\"")}1' exp-OC-lowEduEco2.xml > exp-OC-lowEduEco.xml
rm exp-OC-lowEduEco2.xml