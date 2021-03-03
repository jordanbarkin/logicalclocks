# Logical Clocks Simulation

## Getting Started

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


You can invoke `vm.py` directly with:

```
python3 vm.py <args>
```
That said, starting a single instance is not very interesting.

## Design Decisions

Overall, we did not face too many design difficulties during this assignment. We've enumerated our decisions and their motivations below.

1. The most challenging design question was figuring out how to handle communcation between the various VMs. This was divided into two subproblems:
  - How should the machines discover each other on startup?
  - How should the machines communicate once they are initialized.

  At first, we tried to write an implementation using bare sockets as the method of communication. This led to several challenges:
    - For every pair of machines, it became necessary to figure out which one should `bind` and which should `connect`. It seemed very difficult to do this without either predetermining this in a configuration file and carefully ordering the connection process or running a server to coordinate the other machines. Neither solution seemed ideal.
    - If we chose the first option, it would be challenging to dynamically reconfigure the neivornment to try different tests.

  Once we realized that we could use any libraries we wanted for communication, we switched to an easier approach. Each VM hosts its own web application, using the `Flask` python framework, which it uses to accept messages from any other machine. Machines are uniquely identified by the port on which they are hosted. Now, all a machine needs to know on startup is its own port and a list of the other machines' ports. Each machine exposes an endpoint to receive messages, and sending a message to it just involves making a get request to `localhost:<target_port>/<message>`.

2. Synchronizing the queue within each VM seemed like it might pose a challenge at first, but since Python provides a synchronized, atomic queue in its `queue.Queue`, this behavior was already provided. Since the Flask endpoint executes asynchronously with the virtual machine simulation, no additional synchronization logic was required to handle filling and emptying the queue during the simulation.

3. When designing our experiments, we spent some time considering what data to write to the log. Ultimately, we settled on each machine logging the following fields for each event:
  - The type of event (receive, send, sendall, internal)
  - The current logical clock time
  - The current message queue length
  - The current clock time, which should be consistant across VMs, since they all are running on the same physical machine.

In addition, each log is named with its trial number, port, and clockspeed for identification.

This provides sufficient data for exploring relationships between clock speed, logical time, and physical clock time, as well as the impact on the frequencies of the different event types on simulation behavior.

