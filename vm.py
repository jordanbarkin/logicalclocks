from flask import Flask
import threading
import queue
import requests
import random
import argparse
import csv
import time
import sys

# We host a Flask app to handle incoming messages asynchronously
app = Flask(__name__)

# a queue of this VM's messages to process
message_queue = queue.Queue()

# current logical clock time; starts at 0
logical_clock_time = 0

# startup time, used as origin for log timestamps
start_time = 1000*time.time()

# -------------------Networking--------------------

# Receive an integer at the / endpoint and throw it on the queue.
@app.route('/<time>')
def receive(time):
    global message_queue
    message_queue.put(time)
    # return a nonsense html string so Flask is happy
    return "Received"

# Post a message to localhost:target with the current time.
# Other VMs will be hosted at these different portnums, and identified only
# by their ports.
def send_message(target):
    requests.get(f"http://localhost:{target}/{logical_clock_time}")

# ---------------------Logging--------------------

# Write a header to filename, truncating if the file exists
def setup_log():
   with open(filename, "w+") as f:
      writer = csv.writer(f, delimiter = ",")
      writer.writerow(["event_type", "logical_clock_time", "message_queue_length", "system_time"])

# Write a line to the log representing event at the current time.
def write_action(event):
    with open(filename, "a+") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow([event, logical_clock_time, message_queue.qsize(), int(1000*(time.time())-start_time)])

# ---------------Machine simulation---------------

# Process an event in the queue if it exists.
# Otherwise return None
def try_process_message():
    try:
        message = message_queue.get_nowait()
    except queue.Empty:
        return None

    global logical_clock_time
    logical_clock_time = max(logical_clock_time, int(message)) + 1

    return "received"

# Perform an action with the probabilities from the assignment.
# This is only called if there are no received messages to process in the queue.
def perform_action(test=False):
    global logical_clock_time
    global other_machine__ports

    action = random.randrange(1, 11) # [1,10] inclusive
    logical_clock_time += 1

    # Encode the processing rules
    if action <= 2:
        if not test:
            send_message(random.choice(other_machine_ports))
        return "send"
    elif action == 3:
        if not test:
            for p in other_machine_ports:
                send_message(p)
        return "sendall"
    else:
        return "internal"

# Run a single execution of the machine
def execute_cycle():
    # process received message
    event = try_process_message()

    # if queue is empty, perform an action
    if not event:
        event = perform_action()

    write_action(event)

# run a cycle every (1/rate) seconds
def run_machine():
    while (1000*time.time() <= end_time):
        time.sleep(1/rate)
        execute_cycle()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-port", help="Port for this machine", default=12345)
    parser.add_argument("-trial", help="Log identification only", default=1)
    parser.add_argument('-others', type=int, nargs='+', help="The ports of the other machines", default=[])
    parser.add_argument('-duration', type=int, help="How many seconds to run before exiting", default=60)
    parser.add_argument('-multiplier', type=int, help="Increase the chosen clockspeed by this many times.", default=1)
    parser.add_argument('-overridefreq', type=int, help="Set a manual frequency, overriding the default randomly generated value.", default=None)
    args = parser.parse_args()

    # initial state
    port = int(args.port)
    trial = int(args.trial)
    other_machine_ports = args.others
    rate = (args.overridefreq if args.overridefreq else random.randrange(1, 7))*int(args.multiplier)
    filename = f"trial_{trial}_port_{port}_clockspeed_{rate}hz_internal_probability_0.1.txt"
    duration = args.duration
    end_time = start_time + (1000 * duration)


    # startup logging
    print(f"Running trial {trial} on port {port}. ")
    print(f"Connecting to {str(other_machine_ports)}.")
    print(f"Log will be located at: {filename}.")
    print(f"Picked random clockrate of: {rate}.")

    # Run the web server on a separate thread so that receiving messages is asynchronous
    # with respect to the virtual machine.
    threading.Thread(target=app.run, kwargs={"debug":False, "host":"localhost", "port":port}, daemon=True).start()

    # Initialize logging at filename
    setup_log()

    # Run the machine for -duration seconds
    run_machine()
    time.sleep(3)

    print("Finished. Exiting\n")

    # Kill the webserver when the VM is done.
    sys.exit()
