#!/bin/bash

AGORA=`date +"%Y%m%dT%H%M%S"`

echo Hoje  : $AGORA

#renomear lastest para previous
rm PREVIOUS_static.xml
mv LATEST_static.xml PREVIOUS_static.xml

rm PREVIOUS_static.json
mv LATEST_static.json PREVIOUS_static.json

#ir buscar os ficheiros
wget -O LATEST_static.xml "https://pgm.mobie.pt/integration/nap/evChargingInfra" --no-check-certificate
