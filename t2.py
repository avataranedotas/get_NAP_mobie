#usar pyhton3.6
#pip install lxml
#pip install xmlschema

from lxml import etree
import xmlschema
import json

# Parse the XML file
tree = etree.parse("LATEST_static.xml")
#tree = etree.parse("evChargingInfra.xml")
#tree = etree.parse("teste.xml")
root = tree.getroot()

# Definindo os namespaces corretamente. Todos os elementos têm um prefixo, por isso temos que mapear os namespaces para os respectivos prefixos.
namespace = {
    'ns' : 'http://datex2.eu/schema/3/common',        # Namespace sem prefixo (default)
    'ns2': 'http://datex2.eu/schema/3/locationExtension',
    'ns3': 'http://datex2.eu/schema/3/locationReferencing',
    'ns4': 'http://datex2.eu/schema/3/facilities',
    'ns5': 'http://datex2.eu/schema/3/commonExtension',
    'ns6': 'http://datex2.eu/schema/3/energyInfrastructure',
    'ns7': 'http://datex2.eu/schema/3/d2Payload',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}


# Dicionário para agrupar os dados dos sites
site_data = {}

# Data de actualização
publication_time = root.find('.//ns:publicationTime', namespaces=namespace).text

# Extrair sites
energy_infrastructure_sites = tree.xpath('//ns6:energyInfrastructureSite', namespaces=namespace)

for site in energy_infrastructure_sites:
    # Extrair 'id'
    site_id = site.xpath('@id', namespaces=namespace)[0]
    
    # Extrair name e se for diferente do ID guardar
    name = site.xpath('.//ns4:name/ns:values/ns:value[@lang="pt-pt"]/text()', namespaces=namespace)
    #print (city[0])
    name_texto = str(name[0]) if name else ""
    if name_texto == site_id :
        name_texto = ""

    # Ultima actualizacao
    actual = site.xpath('.//ns4:lastUpdated', namespaces=namespace)
    actual_texto = actual[0].text if actual else "N§A"

    # Extrair a cidade do site
    city = site.xpath('.//ns2:city/ns:values/ns:value[@lang="pt-pt"]/text()', namespaces=namespace)
    #print (city[0])
    city_texto = str(city[0]) if city else "N§A"
    
    # Extrair código postal
    cp = site.xpath('.//ns2:postcode', namespaces=namespace)
    cp_texto = cp[0].text if cp else "N§A"

    # Extrair o texto da rua
    rua = site.xpath('.//ns2:addressLine/ns2:text/ns:values/ns:value[@lang="pt-pt"]/text()', namespaces=namespace)
    rua_texto = str(rua[0]) if rua else "N§A"

    # Extrair a latitude e longitude
    latitude = site.xpath('.//ns3:latitude', namespaces=namespace)
    latitude_texto = latitude[0].text if latitude else "N§A"
    longitude = site.xpath('.//ns3:longitude', namespaces=namespace)
    longitude_texto = longitude[0].text if longitude else "N§A"
    #print (latitude_texto,longitude_texto)
    
    # Extrair o OPC
    opc = site.xpath('.//ns4:nationalOrganisationNumber', namespaces=namespace)
    opc_texto = opc[0].text if opc else "N§A"

    # Extrair o nome do OPC
    opc_nome = site.xpath('.//ns4:operator/ns4:name/ns:values/ns:value[@lang="pt-pt"]/text()', namespaces=namespace)
    opc_nome_texto = str(opc_nome[0]) if opc_nome else "N§A"    

    # Verificar se está aberto 24h
    horas = site.find('ns4:operatingHours[@xsi:type="ns4:OpenAllHours"]',namespaces=namespace)
    if horas is None:
        horas_texto = "Limited hours"
    else:
        horas_texto = "24/7"
    
    # Buscar as estações associadas a esse site
    stations = site.xpath('.//ns6:energyInfrastructureStation', namespaces=namespace)
    
    # Listar e procurar dentro das estações associadas a este site
    station_data = []
    cs=0
    for station in stations:
        station_id = station.xpath('@id', namespaces=namespace)[0]
        station_data.append({'station_id': station_id})

        # Verificar se tem amenities associadas
        assfac = station.findall('.//ns4:associatedFacility', namespaces=namespace)
        assfac_matriz = []
        for facility in assfac:
            facility_type = facility.find('./ns4:type', namespaces=namespace)
            if facility_type is not None:
                assfac_matriz.append(facility_type.text)

        # Adicionalmente verificar se tem mais amenities
        amenity = station.findall('.//ns4:serviceFacilityType', namespaces=namespace)
        for facility in amenity:
            if facility is not None and facility.text != "other":
                assfac_matriz.append(facility.text)                

        # Adicionalmente verificar se tem nome nas facilities do tipo other
        others = station.findall('.//ns4:supplementalFacility[ns4:serviceFacilityType="other"]', namespaces=namespace)
        for facility in others:
            name_element = facility.xpath('.//ns:values/ns:value[@lang="pt-pt"]/text()', namespaces=namespace)
            if name_element is not None:
                assfac_matriz.append(name_element[0])
 
        if assfac_matriz != []:
            station_data[cs]["facilities"] = assfac_matriz


        #Listar os meios de pagamento da estação
        meios = station.findall('.//ns6:authenticationAndIdentificationMethods', namespaces=namespace)
        #print (meios)
        meios_matriz = []

        if meios is not None:
            meios_matriz = [metodo.text for metodo in meios]

        if meios_matriz != []:
            station_data[cs]["payment"] = meios_matriz
                       
        # Buscar evse associadas a esta estação
        evses = station.xpath('.//ns6:refillPoint', namespaces=namespace)
    
        if evses is not None:
            station_data[cs]["evses"] = []
        for evse in evses:
            evse_id = evse.xpath('ns4:externalIdentifier', namespaces=namespace)
            evse_id_texto = evse_id[0].text if evse_id else "N§A"
            
            # Adicionar aqui extração de preços se for necessário
   


            # Dentro de cada EVSE há vários conectores

            connectors = evse.xpath('.//ns6:connector', namespaces=namespace)
            connector_details = []
            
            for connector in connectors:
                connector_type = connector.find('ns6:connectorType', namespaces=namespace)
                charging_mode = connector.find('ns6:chargingMode', namespaces=namespace)
                max_power = connector.find('ns6:maxPowerAtSocket', namespaces=namespace)
                voltage = connector.find('ns6:voltage', namespaces=namespace)
                max_current = connector.find('ns6:maximumCurrent', namespaces=namespace)

                connector_details.append({
                    'connector_type': connector_type.text if connector_type is not None else "N§A",
                    'charging_mode': charging_mode.text if charging_mode is not None else "N§A",
                    'max_power': max_power.text if max_power is not None else "N§A",
                    'voltage': voltage.text if voltage is not None else "N§A",
                    'max_current': max_current.text if max_current is not None else "N§A"
                })

            evse_info = {
                "evse_id": evse_id_texto,
                "connectors": connector_details
            }
            station_data[cs]["evses"].append(evse_info)

        cs=cs+1
    
    
    # Armazenar as informações no dicionário agrupadas por site
    site_data[site_id] = {
        'name': name_texto,
        'lastUpdated' : actual_texto,
        'city': city_texto,
        'street': rua_texto,
        'postcode' : cp_texto,
        'latitude': latitude_texto,
        'longitude': longitude_texto,
        'opc': opc_texto,
        'opc_name': opc_nome_texto,
        'hours' : horas_texto,
        'stations': station_data
    }
    
    
    
    
    
#print ("--------DEBUG-------")
#print (site_data.get("CSC-00235"))
#print (type(site_data.get("CSC-00235").get("stations")))
#print (site_data)
#print ("--------DEBUG-------")



def display_station_info(evse_data):
    for evse in evse_data:
        print(f"  EVSE: {evse['evse_id']}")
        for connector in evse["connectors"]:
            print(
                f"   Tomada: {connector['connector_type']} {connector['charging_mode']} {connector['max_power']} {connector['voltage']} {connector['max_current']}"
            )

# Print dos resultados agrupados por site

print ("---")
for site_id,data in site_data.items():
    print(f"Local: {site_id} {data['latitude']} {data['longitude']} {data['hours']} {data['opc']} {data['opc_name']}" )
    print(f"       {data['name']} {data['street']} {data['postcode']} {data['city']}" )
    for yy in data['stations']:
        #print ("dentro stations")
        #print (type (yy))
        #print (yy)
        if "station_id" in yy:
            print (f" Posto: {yy.get('station_id')}")
        if "facilities" in yy:
            print (f" Facilities: {yy.get('facilities')}")
        if "payment" in yy:
            print (f" Payment: {yy.get('payment')}")
        if "evses" in yy:
            display_station_info (yy.get('evses'))
    print ("---")



# Exportar para json

json_file_path = 'LATEST_static.json'

with open(json_file_path, 'w') as json_file:
    json.dump(site_data, json_file, indent=4)




