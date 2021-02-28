from flask import Flask
import threading
import queue
import requests
import random
import argparse
import csv
import time

app = Flask(__name__)
message_queue = queue.Queue()
logical_clock_time = 0
rate = random.randrange(1, 7)
start_time = 1000*time.time()

# Networking
@app.route('/<time>')
def receive(time):
    global message_queue
    message_queue.put(time)
    return "Received"

def send_message(target):
    requests.get(f"http://localhost:{target}/{logical_clock_time}")

# Logging
def setup_log():
   with open(filename, "w+") as f:
      writer = csv.writer(f, delimiter = ",")
      writer.writerow(["event_type", "logical_clock_time", "message_queue_length", "system_time"])

def write_action(event):
    with open(filename, "a+") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow([event, logical_clock_time, message_queue.qsize(), int(1000*(time.time())-start_time)])

# Machine simulation
def try_process_message():
    try:
        message = message_queue.get_nowait()
    except queue.Empty:
        return None

    global logical_clock_time
    logical_clock_time = max(logical_clock_time, int(message)) + 1

    return "received"

def perform_action():
    global logical_clock_time
    global other_machine__ports

    action = random.randrange(0, 10)
    logical_clock_time += 1

    if action <= 1:
        send_message(random.choice(other_machine_ports))
        return "send"
    elif action == 2:
        for p in other_machine_ports:
            send_message(p)
        return "multisend"
    else:
        return "internal"

def execute_cycle():
    event = try_process_message()

    if not event:
        event = perform_action()

    write_action(event)

def run_machine():
    while (1000*time.time() <= end_time):
        time.sleep(1/rate)
        execute_cycle()

# args and main routine
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-port", help="Port for this machine", default=-1)
    parser.add_argument("-trial", help="Log identification only", default=1)
    parser.add_argument('-others', type=int, nargs='+', help="The ports of the other machines")
    parser.add_argument('-duration', type=int, nargs='+', help="How many seconds to run before exiting", default=60)

    args = parser.parse_args()

    port = int(args.port)
    trial = int(args.trial)
    other_machine_ports = args.others
    filename = f"trial_{trial}_port_{port}_clockspeed_{rate}hz.txt"
    duration = args.duration
    end_time = start_time + (1000 * duration)

    print(f"Running trial {trial} on port {port}. ")
    print(f"Connecting to {str(other_machine_ports)}.")
    print(f"Log will be located at: {filename}.")
    print(f"Picked random clockrate of: {rate}.")

    threading.Thread(target=app.run, kwargs={"debug":False, "host":"localhost", "port":port}).start()
    
    setup_log()
    run_machine()
    print("Finished. Exiting")