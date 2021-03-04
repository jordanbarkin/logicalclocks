from vm import *

# We unit test the basic functionality of our machine here.
def test_queue():
  # test the web endpoint
  receive(1)
  receive(2)
  receive(3)
  receive(4)
  receive(5)

  # validate queue behavior
  r = try_process_message()
  assert r == "received"
  r = try_process_message()
  assert r == "received"
  r = try_process_message()
  assert r == "received"
  r = try_process_message()
  assert r == "received"
  r = try_process_message()
  assert r == "received"
  r = try_process_message()
  assert r == None


# Unit test machine mechanics
def test_execute_cycle():
  # test the web endpoint
  receive(1)
  receive(2)
  receive(3)
  receive(4)
  receive(5)

  # check that the distribution is right
  send = 0
  sendall = 0
  internal = 0
  receive_count = 0

  # check that cycles behave as expected
  for i in range(10005):
    action = try_process_message()
    if not action:
        action = perform_action(test=True)

    if action == "send":
      send += 1
    elif action == "sendall":
      sendall += 1
    elif action == "received":
      receive_count += 1
    elif action == "internal":
      internal += 1
    else:
      assert False

  # check that frequencies are within 10% of expected values
  assert receive_count == 5
  assert abs(0.1 - (sendall/10000)) <= 0.1
  assert abs(0.2 - (send/10000)) <= 0.1
  assert abs(0.7 - (internal/10000)) <= 0.1

if __name__ == '__main__':
  test_queue()
  test_execute_cycle()

