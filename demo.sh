counter=1
while [ $counter -le 5 ]
do
    python3 ./vm.py -trial $counter -port 12345 -others 12346 12347 &
    python3 ./vm.py -trial $counter -port 12346 -others 12345 12347 &
    python3 ./vm.py -trial $counter -port 12347 -others 12345 12346 
    ((counter++))
done