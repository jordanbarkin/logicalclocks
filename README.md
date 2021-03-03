# logicalclocks
For CS262 second programming assignment.

`vm.py` contains the virtual machine simulator. It has the following CLI interface:

```
  -h, --help            Show this help message and exit
  -port PORT            Port for this machine to run on
  -trial TRIAL          Trial number for log identification only
  -others OTHERS [OTHERS ...]
                        A list of ports on which other machines are running.
  -duration DURATION    How many seconds to run before exiting.
  -multiplier MULTIPLIER
                        Increase the randomly chosen clockspeed by this MULTIPLIER factors.
  -overridefreq FREQ    Instead of randomly generating a clockspeed, use this frequency (times multiplier).
```

To run a simulation, simultaneously start a few instances of `vm.py` with the above parameters specified. Make sure to tell each vm about the others using the `-others` flag. `demo.sh` provides an example of a shell script that does this. It runs 3 vms on different ports for 5 trials of 1 minute each.
