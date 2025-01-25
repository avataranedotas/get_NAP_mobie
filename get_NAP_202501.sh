#!/bin/bash

AGORA=`date +"%Y%m%dT%H%M%S"`

echo Hoje  : $AGORA

#renomear lastest para previous
#rm PREVIOUS_static.json
#mv LATEST_static.json PREVIOUS_static.json
#rm PREVIOUS_dynamic.json
#mv LATEST_dynamic.json PREVIOUS_dynamic.json

#ir buscar os ficheiros
wget -O LATEST_static.xml "https://pgm.mobie.pt/integration/nap/evChargingInfra" --no-check-certificate
#wget -O LATEST_dynamic.json "https://idacs.mobinteli.com/datex/dynamic" --no-check-certificate
