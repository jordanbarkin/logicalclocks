counter=1
while [ $counter -le 5 ]
do
    python3 ./vm.py -multiplier 1 -trial $counter -port 12345 -others 12346 12347 -duration 60 &
    python3 ./vm.py -multiplier 1 -trial $counter -port 12346 -others 12345 12347 -duration 60 &
    python3 ./vm.py -multiplier 1 -trial $counter -port 12347 -others 12345 12346 -duration 60
    ((counter++))
done
