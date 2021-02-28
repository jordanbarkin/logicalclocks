python3 ./vm.py -port 12345 -others 12346 12347 &
python3 ./vm.py -port 12346 -others 12345 12347 &
python3 ./vm.py -port 12347 -others 12345 12346