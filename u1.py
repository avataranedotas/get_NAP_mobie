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

# Extrair status dos sites
energy_status_sites = root.findall('.//ns3:energyInfrastructureSiteStatus', namespaces=namespace)

for site in energy_status_sites:
    # Extrair 'id'
    site_id = site.find("ns2:reference", namespaces=namespace).get("id")
    #print (site_id)
    

    # Procurar estações dentro do site
    stations = site.xpath('.//ns3:energyInfrastructureStationStatus', namespaces=namespace)
    station_data = []
    cs=0

    for station in stations:
        station_id = station.find("ns2:reference", namespaces=namespace).get("id")
        #print (station_id)
        station_data.append({'station_id': station_id})

        # Buscar status evse associadas a esta estação
        evses = station.xpath('.//ns3:refillPointStatus', namespaces=namespace)
        evse_data = []
        ce=0
        for evse in evses:
            evse_id = evse.find("ns2:reference", namespaces=namespace).get("id")
            evse_data.append({'evse_id': evse_id})
            
            evse_status = evse.find("ns3:status", namespaces=namespace).text
            #print (evse_status)
            evse_data[ce]["evse_status"] = evse_status
            ce=ce+1

        station_data[cs]["evses"] = evse_data
        cs=cs+1

    # Armazenar as informações no dicionário agrupadas por site
    status_data[site_id] = {
        'lastUpdated' : publication_time,
        'stations': station_data
    }
    
    
    
    
    
#print ("--------DEBUG-------")
#print (status_data)
#print ("--------DEBUG-------")




def display_station_info(evse_data):
    for evse in evse_data:
        print(f"  EVSE: {evse['evse_id']} {evse['evse_status']}")



# Print dos resultados agrupados por site

#print ("---")
#for site_id,data in status_data.items():
#    print(f"Local: {site_id}" )
#    for yy in data['stations']:
#        if "station_id" in yy:
#            print (f" Posto: {yy.get('station_id')}")
#        if "evses" in yy:
#            display_station_info (yy.get('evses'))
#    print ("---")




# Exportar para json

json_file_path = 'LATEST_dynamic.json'
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(status_data, json_file, indent=4, ensure_ascii=False)


