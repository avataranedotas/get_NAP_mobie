#!/bin/bash

AGORA=`date +"%Y%m%dT%H%M%S"`

echo Hoje  : $AGORA

#renomear lastest para previous
rm PREVIOUS_dynamic.xml
mv LATEST_dynamic.xml PREVIOUS_dynamic.xml

rm PREVIOUS_dynamic.json
mv LATEST_dynamic.json PREVIOUS_dynamic.json

#ir buscar os ficheiros
wget -O LATEST_dynamic.xml "https://pgm.mobie.pt/integration/nap/evActualStatus" --no-check-certificate
