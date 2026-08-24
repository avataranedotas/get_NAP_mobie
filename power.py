import json
import csv

# Load your JSON file
with open('LATEST_static.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Prepare list to store filtered rows
rows = []

# Prepare CSV output
with open('power_table.csv', 'w', newline='', encoding='utf-8') as csvfile, \
     open('power_table.tsv', 'w', newline='', encoding='utf-8') as tsvfile:
    writer = csv.writer(csvfile, delimiter=';')
    tsb_writer = csv.writer(tsvfile, delimiter='\t')
    
    # Write header
    writer.writerow([
        'Station ID', 'OPC', 'EVSE ID', 'Connector Type', 'Charging Mode',
        'Voltage (V)', 'Max Current (A)', 'Calculated Power (W)', 'Claimed Power (W)', 'Power Difference (W)'
    ])
    
    # Write header
    tsb_writer.writerow([
        'Plug ID', 'OPC', 'EVSE ID', 'Connector Type', 'Charging Mode',
        'Voltage (V)', 'Max Current (A)', 'Calculated Power (W)', 'Claimed Power (W)', 'Power Difference (W)'
    ])

    # Write connector rows
    for station in data.values():
        for station_entry in station.get('stations', []):
            station_id = station_entry.get('station_id')
            for evse in station_entry.get('evses', []):
                evse_id = evse.get('evse_id')
                for connector in evse.get('connectors', []):
                    voltage = float(connector.get('voltage', 0))
                    current = float(connector.get('max_current', 0))
                    max_power = float(connector.get('max_power', 0))
                    charging_mode = connector.get('charging_mode', '')
                    connector_type = connector.get('connector_type')
                    evse_code_3letter = evse_id.split('*')[1] if '*' in evse_id else ''

                    # Custom calculation 
                    if charging_mode == "mode3AC3p":
                        calc_power = round(240 * current * 3, -2)
                    elif charging_mode == "mode2AC1p":
                        calc_power = round(240 * current , -2)
                    else:
                        calc_power = round(voltage * current, -2)

                    # Power difference
                    power_diff = calc_power - max_power

                    # Apply filter
                    write_row = False
                    if charging_mode in ("mode3AC3p", "mode2AC1p") and power_diff < -200:
                        write_row = True
                    elif charging_mode == "mode4DC" and power_diff < -2000:
                        write_row = True

                    if write_row:
                        rows.append([
                        #writer.writerow([
                            station_id,
                            evse_code_3letter,
                            evse_id,
                            connector_type,
                            charging_mode,
                            f"{voltage:.1f}",
                            f"{current:.1f}",
                            f"{calc_power:.1f}",
                            f"{max_power:.1f}",
                            f"{power_diff:.1f}"
                        ])


    # Sort by power_diff (last column, index -1)
    rows.sort(key=lambda r: float(r[-1]))

    writer.writerows(rows)
    tsb_writer.writerows(rows)
