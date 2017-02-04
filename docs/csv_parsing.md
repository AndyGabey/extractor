CSV Parsing
===========

MM 4/2/2017:
I've tested 3 parsing options: manual (readlines combined with split), csv (std lib),
pandas.read\_csv)
Results are in ../experiments/csv\_parse\_results.out
Upshot is that manual, csv both use about 75% of the memory of pandas, and run in half the time.
Another bonus is that it will be easy to stop streaming when e.g. the desired end date is found.
Given that manual and csv both use around the same time/mem, and csv comes with a lot of bonuses, I
think it makes sense to use this library for the parsing.

N.B. I think it should be possible to use the f.seek(offset) trick with this lib too. This is where
e.g. start time offsets are pre-calc'd and the file can be opened at the correct loc.

MM 4/2/2017:
Test 2: if you're only grabbing certain vars from the CSV (e.g. RH, P) time and mem come down
dramatically again using csv vs pandas. pandas is more or less as it was but csv now uses 10 MB as
opposed to pandas' 270 MB. Clear winner here as well. It will mean that I have to do the conversion
to json myself but hopefully this won't be too bad.

