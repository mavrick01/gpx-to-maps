import sys
import xml.etree.ElementTree as ET

def generate_google_maps_link(file_path):
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # GPX files use namespaces. We need to find the namespace from the root tag.
        # It usually looks like {http://www.topografix.com/GPX/1/1}
        ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

        # Find all 'rtept' (route point) entries
        route_points = root.findall('.//gpx:rtept', ns)

        if not route_points:
            print("No route points (rtept) found in the file.")
            return

        # Extract lat/lon and format them as 'lat,lon' strings
        coords = []
        for pt in route_points:
            lat = pt.get('lat')
            lon = pt.get('lon')
            if lat and lon:
                coords.append(f"{lat},{lon}")

        # Construct the Google Maps Directions URL
        base_url = "https://www.google.com/maps/dir/"
        final_url = base_url + "/".join(coords)

        print("\nGenerated Google Maps Link:")
        print(final_url)

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except ET.ParseError:
        print("Error: Failed to parse the XML. Ensure it is a valid GPX file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gpx_to_maps.py <filename.gpx>")
    else:
        generate_google_maps_link(sys.argv[1])
