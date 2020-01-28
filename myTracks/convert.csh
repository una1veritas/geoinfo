#!/bin/csh
foreach f(*.gpx)
    python3 gpxreader -mjd "$f"
end
