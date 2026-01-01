import sys
import xml.etree.ElementTree as ET

def generate_google_maps_link(file_path):
    # Standard browser/URL limit is 2000. 
    # We use 1850 as a safe threshold to avoid "URL too long" errors.
    CHAR_LIMIT = 1850
    BASE_URL = "https://www.google.com/maps/dir/"
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {
            'gpx': 'http://www.topografix.com/GPX/1/1',
            'gpxx': 'http://www.garmin.com/xmlschemas/GpxExtensions/v3'
        }

        # 1. Extract mandatory waypoints (rtept)
        rtepts = root.findall('.//gpx:rtept', ns)
        mandatory_coords = [f"{p.get('lat')},{p.get('lon')}" for p in rtepts]
        
        # 2. Extract all detailed path points (gpxx:rpt)
        # We store them in a way that relates them to their segments if needed, 
        # but for a single route, a flat list works as long as we deduplicate.
        all_rpt_pts = root.findall('.//gpxx:rpt', ns)
        filler_coords = [f"{p.get('lat')},{p.get('lon')}" for p in all_rpt_pts]
        
        # Remove points that are already in mandatory_coords to avoid duplication
        mandatory_set = set(mandatory_coords)
        filler_coords = [c for c in filler_coords if c not in mandatory_set]

        # 3. Calculate Character Budget
        # Length used by base URL and mandatory points (plus slashes)
        current_len = len(BASE_URL) + sum(len(c) + 1 for c in mandatory_coords)
        remaining_space = CHAR_LIMIT - current_len

        if remaining_space <= 0:
            # If waypoints alone are too many (rare), just use them
            final_coords = mandatory_coords
        else:
            # Calculate how many filler points we can fit
            # Average coordinate "-46.12345,6.12345" is ~20 chars + 1 slash
            max_fillers = remaining_space // 21
            
            if len(filler_coords) <= max_fillers:
                # We can fit all of them
                final_coords = mandatory_coords + filler_coords
            else:
                # Thin the fillers specifically
                # We use a step to pick every nth filler point
                step = len(filler_coords) // max_fillers
                # Ensure step is at least 1
                step = max(1, step)
                thinned_fillers = filler_coords[::step]
                
                # Combine them. Note: For Google Maps 'dir', order matters.
                # Since gpxx:rpt in your file are usually sequential, 
                # we combine and sort based on original file order if necessary,
                # but appending fillers to mandatory often breaks the 'path'.
                
                # BETTER APPROACH: Interleave them or just thin the WHOLE clean list
                # but PROTECT the mandatory ones.
                
                all_ordered_clean = []
                # Re-parse to keep sequence: Waypoint -> its path -> Waypoint -> its path
                for rtept in rtepts:
                    coord = f"{rtept.get('lat')},{rtept.get('lon')}"
                    all_ordered_clean.append((coord, True)) # (coord, is_mandatory)
                    
                    rpts = rtept.findall('.//gpxx:rpt', ns)
                    for rpt in rpts:
                        r_coord = f"{rpt.get('lat')},{rpt.get('lon')}"
                        if r_coord != coord:
                            all_ordered_clean.append((r_coord, False))

                # Now thin the non-mandatory ones
                final_coords_list = []
                # Calculate global step for non-mandatory points
                total_fillers = sum(1 for _, is_m in all_ordered_clean if not is_m)
                filler_step = max(1, total_fillers // max_fillers)
                
                filler_count = 0
                for coord, is_mandatory in all_ordered_clean:
                    if is_mandatory:
                        final_coords_list.append(coord)
                    else:
                        if filler_count % filler_step == 0:
                            final_coords_list.append(coord)
                        filler_count += 1
                
                final_coords = final_coords_list

        # 4. Final safety check: if still too long, increase thinning
        while len(BASE_URL) + sum(len(c) + 1 for c in final_coords) > CHAR_LIMIT and len(final_coords) > len(mandatory_coords):
            # Remove one filler from the middle until it fits
            for i in range(len(final_coords)-1, 0, -1):
                if final_coords[i] not in mandatory_set:
                    final_coords.pop(i)
                    break

        final_url = BASE_URL + "/".join(final_coords)
        
        print(f"Mandatory points: {len(mandatory_coords)}")
        print(f"Filler points added: {len(final_coords) - len(mandatory_coords)}")
        print(f"Total URL Length: {len(final_url)}")
        print("\nGenerated Link:")
        print(final_url)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <file.gpx>")
    else:
        generate_google_maps_link(sys.argv[1])
