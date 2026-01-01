# GPX to Google Maps

A simple python script to read a gpx file and output a URL.

I have 2 versions
- Basic : Reads the gpx file and only looks at the `<rtept>` tags
- Advanced  : This one reads the `<rtept>` tags and then fills in any waypoints given using the `<gpxx:rpt>` tags

