CSV Parsing
===========

MM:
I've tested 3 parsing options: manual (readlines combined with split), csv (std lib),
pandas.read\_csv)
Results are in ../experiments/csv\_parse\_results.out
Upshot is that manual, csv both use about 75% of the memory of pandas, and run in half the time.
Another bonus is that it will be easy to stop streaming when e.g. the desired end date is found.
Given that manual and csv both use around the same time/mem, and csv comes with a lot of bonuses, I
think it makes sense to use this library for the parsing.

N.B. I think it should be possible to use the f.seek(offset) trick with this lib too. This is where
e.g. start time offsets are pre-calc'd and the file can be opened at the correct loc.

