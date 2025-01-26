#usar pyhton3.6
#pip install lxml


from lxml import etree
import json

# Parse the XML file
tree = etree.parse("LATEST_dynamic.xml")
#tree = etree.parse("evActualStatus.xml")
#tree = etree.parse("status1.xml")
root = tree.getroot()

# Definindo os namespaces corretamente. Todos os elementos têm um prefixo, por isso temos que mapear os namespaces para os respectivos prefixos.
namespace = {
    'ns' : 'http://datex2.eu/schema/3/common',        # Namespace sem prefixo (default)
    'ns2': 'http://datex2.eu/schema/3/facilities',
    'ns3': 'http://datex2.eu/schema/3/energyInfrastructure',
    'ns4': 'http://datex2.eu/schema/3/d2Payload'
}


# Dicionário para agrupar os dados dos sites
status_data = {}

# Data de actualização
publication_time = root.find('.//ns:publicationTime', namespaces=namespace).text
print (publication_time)

lista_uso = []
lista_uso_stations = []


# Extrair status dos sites
energy_status_sites = root.findall('.//ns3:energyInfrastructureSiteStatus', namespaces=namespace)

for site in energy_status_sites:
    # Extrair 'id'
    site_id = site.find("ns2:reference", namespaces=namespace).get("id")
 

    # Procurar estações dentro do site
    stations = site.xpath('.//ns3:energyInfrastructureStationStatus', namespaces=namespace)
    cs=0

    for station in stations:
        station_id = station.find("ns2:reference", namespaces=namespace).get("id")

        # Buscar status evse associadas a esta estação
        evses = station.xpath('.//ns3:refillPointStatus', namespaces=namespace)
        ce=0
        for evse in evses:
            evse_id = evse.find("ns2:reference", namespaces=namespace).get("id")
            evse_status = evse.find("ns3:status", namespaces=namespace).text
            if evse_status == "charging" :
                lista_uso.append(evse_id)
                lista_uso_stations.append(station_id)
            ce=ce+1

        cs=cs+1

    
#print ("--------DEBUG-------")
#print (lista_uso)
#print (lista_uso_stations)
#print ("--------DEBUG-------")


# Exportar para texto

file_path = "inuse.txt"

with open(file_path, "w", encoding="utf-8") as file:
    for line in lista_uso:
        file.write(line + "\n")

file_path = "inuse_stations.txt"

with open(file_path, "w", encoding="utf-8") as file:
    for line in lista_uso_stations:
        file.write(line + "\n")


