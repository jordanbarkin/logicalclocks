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
    - If we chose the first option, it would be challenging to dynamically reconfigure the enivornment to try different tests.

  Once we realized that we could use any libraries we wanted for communication, we switched to an easier approach. Each VM hosts its own web application, using the `Flask` python framework, which it uses to accept messages from any other machine. Machines are uniquely identified by the port on which they are hosted. Now, all a machine needs to know on startup is its own port and a list of the other machines' ports. Each machine exposes an endpoint to receive messages, and sending a message to it just involves making a get request to `localhost:<target_port>/<message>`.

2. Synchronizing the queue within each VM seemed like it might pose a challenge at first, but since Python provides a synchronized, atomic queue in its `queue.Queue`, this behavior was already provided. Since the Flask endpoint executes asynchronously with the virtual machine simulation, no additional synchronization logic was required to handle filling and emptying the queue during the simulation.

3. When designing our experiments, we spent some time considering what data to write to the log. Ultimately, we settled on each machine logging the following fields for each event:
  - The type of event (receive, send, sendall, internal)
  - The current logical clock time
  - The current message queue length
  - The current clock time, which should be consistent across VMs, since they all are running on the same physical machine.

In addition, each log is named with its trial number, port, and clockspeed for identification.

This provides sufficient data for exploring relationships between clock speed, logical time, and physical clock time, as well as the impact on the frequencies of the different event types on simulation behavior.

## Analysis

`plotter.py` contains a script used to generate plots for the generated data files. If needed, it can be invoked to re-generate plots with:

```
python3 plotter.py
```

The plots are available as pngs in the `data/` folder, with their corresponding tables. 

### Nominal Speed

Observing the plots generated for each trial in the case of nominal (1x) speed, we observe the following:

1. When the system's machines are close in speed to each other, the logical clocks all appear to stay relatively well synchronized. In other words, the logical clock -- system clock function for each machine appears to have a similar slope for each machine. In this case, we also note that the message queue length appears to never increase past one for each machine, suggesting that each machine is able to handle a message before being sent another. This suggests that as long as the machines can keep up with each other, they will be able to maintain relatively well synchronized logical clocks.

2. When the system contains two faster machines of a similar speed and a slower machine (e.g. 1 Hz, 5 Hz, and 5 Hz), the two faster machines appear to remain relatively well synchronized. However, the slower machine appears to experience significant clock drift, running a logical clock that runs slower (i.e. steeper slope with respect to system clock) than the logical clocks of the faster machines, and with a less consistent rate (i.e. the slope is very jittery). This jives well with the observation that the message queue of the slower machine grows continuously -- it cannot keep up with the rate it is receiving messages from the faster machines. The slower machine quickly falls behind the other machines, constantly reacting to outdated logical clock values of the faster machines -- this causes the increased jerkiness and the slower logical clock.

3. When the system contains two slower machines of a similar speed and a faster machine (e.g. 3 Hz, 6 Hz, 3 Hz), the logical clocks all appear to stay reasonably synchronized. However, the progression of the logical clocks of the two slower machines is much jerkier, with more frequent jumps in logical clock value. This behavior makes sense given the previous observation -- the slower machines have difficulty keeping up with the faster machine. However, the new presence of another machine at the slower rate allows the machines to stay synchronized -- the slower machines can easily keep up with each other, even if they cannot keep up as easily with the faster machine. We also note that the increased jitter in the logical clocks of the slower machines appears to correspond with a greater frequency of the message queue length becoming one (and sometimes greater). The faster machine's logical clock is not very jittery, which corresponds with this machine's message queue length rarely being 1, and normally being empty -- this machine is effectively dominating how the logical clocks are set across the entire system.

4. The speed of the (synchronized) logical clocks appear to be most heavily driven by the fastest running machine. In other words, the presence of a 6 Hz machine appears to allow the logical clocks to progress further over 60 seconds than if the fastest machine only runs at 5 Hz. This is a reasonable observation that naturally arises from the logical clock update rules. Note that the presence of slower machines, assuming the system is still able to remain reasonably synchronized, does appear to slow down the progression of the logical clock somewhat.


### Scaled Speed

We then ran similar tests with the possible choices of frequency scaled up from the nominal range of 1 Hz - 6 Hz by 10x (10 Hz - 60 Hz) and 100x (100 Hz - 600 Hz).

We generally observe the same behavior as the nominal case. However we also observe:

1. The effect of previously observed jitter in the logical clock progression caused by mismatched machine rates appears to be significantly lessened as the range of machine speeds is scaled up. Intuitively this makes sense -- much less system time passes between each logical clock update, which causes a "smoothing" effect on the logical clock time-system time plots.

2. The case with two similarly speedy machines with a slow machine progresses as before, with the two faster machines staying well synchronized and the slower machine falling behind on messages, maintaining a slower logical clock. However, the logical clock of the slower machine does not appear to fall behind nearly as much, in a relative sense. We suspect that this is driven by the fact that the logical clocks are updated at a faster rate relative to the true, system time.


### Modifying Probability of Internal Events

Finally, we ran additional tests with machines at similar frequencies (7 Hz, 8 Hz, 9 Hz) while varying the probability of internal events. We experimented with the probability of internal events set to 0.5 and to 0.1. We observed:

1. As the machines are operating at similar frequencies, they are able to maintain reasonable logical clock synchronization.

2. Decreasing the probability of internal events appeared to largely affect message queue traffic -- non-empty message queues appeared to become a more frequent occurrence and message queues tended to fill up with more messages (i.e. the max size of the message queue over the simulated minute increased). This makes sense -- less frequent internal events implies more messages being sent between the machines, increasing network traffic and message queue load.

3. It also appears that the decreased rate of internal events leads to less jittery logical clock progression (this is more pronounced when comparing with the nominal rate case). This effect makes sense -- the machines are communicating more frequently about the state of their logical clocks, directly limiting the skew that can exist and drift that develops between the machine's logical clocks before an update can occur. The jumps in logical clock value that will occur are naturally smaller (and therefore the logical clocks are less jittery) as the machines are communicating more frequently.
