import json
import urllib.request
from pathlib import Path
import csv

from math import radians, sin, cos, sqrt, atan2

TODOS_URL = "https://raw.githubusercontent.com/avataranedotas/umap_postos/refs/heads/main/Todos.json"

TODOS_FILE = Path("Todos.json")
LATEST_FILE = Path("LATEST_static_filtered.json")

EARTH_RADIUS = 6371000.0  # metros

def download_todos():
    """Descarrega o ficheiro Todos.json."""
    print("Downloading Todos.json...")
    urllib.request.urlretrieve(TODOS_URL, TODOS_FILE)
    print("Done.\n")


def load_nap():
    """
    Lê o ficheiro LATEST_static_filtered.json e devolve:

    {
        station_id: (prefix, latitude, longitude)
    }
    """

    nap = {}

    with open(LATEST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for location in data.values():

        latitude = float(location["latitude"])
        longitude = float(location["longitude"])

        for station in location.get("stations", []):

            full_station_id = station["station_id"]

            prefix = full_station_id[:3]      # ACC, EDP, ...
            station_id = full_station_id[4:]  # GRD-00044, LSB-90050, ...

            nap[station_id] = (
                prefix,
                latitude,
                longitude
            )

    return nap


def load_osm():
    """
    Lê Todos.json e devolve:
    {
        ref: (latitude, longitude)
    }

    Apenas considera elementos:
      - type == "node"
      - que possuam a tag "ref"
    """

    osm = {}

    with open(TODOS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for element in data.get("elements", []):

        if element.get("type") != "node":
            continue

        tags = element.get("tags", {})
        ref = tags.get("ref")

        if not ref:
            continue

        location = tags.get("location", "surface")

        osm[ref] = (
            float(element["lat"]),
            float(element["lon"]),
            location
        )

    return osm


def print_memory(title, memory):
    print(f"===== {title} ({len(memory)} entries) =====")

    for station_id, (prefix, lat, lon) in sorted(memory.items()):
        print(f"{prefix:3} {station_id:15} {lat:.7f} {lon:.7f}")

    print()


def build_agg(nap, osm):

    agg = {}

    for ref, (osm_lat, osm_lon, location) in osm.items():

        if ref not in nap:
            continue

        prefix, nap_lat, nap_lon = nap[ref]

        agg[ref] = (
            prefix,
            nap_lat,
            nap_lon,
            osm_lat,
            osm_lon,
            distance_m(nap_lat, nap_lon, osm_lat, osm_lon),
            location
        )

    return agg

def print_agg(agg):

    print(f"===== AGG ({len(agg)} entries) =====")

    for ref, (
        prefix,
        nap_lat,
        nap_lon,
        osm_lat,
        osm_lon,
        distance,
        location
    ) in sorted(
        agg.items(),
        key=lambda item: item[1][5],
        reverse=True
    ):
        print(
            f"{prefix:3} {ref:15} "
            f"NAP=({nap_lat:.7f}, {nap_lon:.7f}) "
            f"OSM=({osm_lat:.7f}, {osm_lon:.7f}) "
            f"{distance:7.2f} m "
            f"LOCATION={location}"
        )

    print()

def distance_m(lat1, lon1, lat2, lon2):
    """Distância entre duas coordenadas GPS em metros."""

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return EARTH_RADIUS * c


def save_agg_tsv(agg, filename="compare_GPS.tsv"):
    """
    Guarda a memória AGG num ficheiro TSV.
    """

    with open(filename, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f, delimiter="\t")

        # Cabeçalho
        writer.writerow([
            "CPO",
            "REF",
            "LAT NAP",
            "LON NAP",
            "LAT OSM",
            "LON OSM",
            "DIST (m)",
            "LOCATION"
        ])

        # Ordenado da maior para a menor distância
        for ref, (
            prefix,
            nap_lat,
            nap_lon,
            osm_lat,
            osm_lon,
            distance,
            location
        ) in sorted(
            agg.items(),
            key=lambda item: item[1][5],
            reverse=True
        ):
            writer.writerow([
                prefix,
                ref,
                f"{nap_lat:.7f}",
                f"{nap_lon:.7f}",
                f"{osm_lat:.7f}",
                f"{osm_lon:.7f}",
                f"{distance:.2f}",
                location
            ])

    print(f"Written {len(agg)} entries to {filename}")


def main():
    download_todos()

    nap = load_nap()
    osm = load_osm()
    
    agg = build_agg(nap, osm)

    #print_memory("NAP", nap)
    #print_memory("OSM", osm)
    #print_agg(agg)
    save_agg_tsv(agg)


if __name__ == "__main__":
    main()
