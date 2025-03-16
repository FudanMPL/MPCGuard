#!/usr/bin/env bash

echo SECURE = -DINSECURE >> CONFIG.mine
touch -r CONFIG CONFIG.mine
touch ECDSA/Fake-ECDSA.cpp

make -j4 ecdsa Fake-ECDSA.x

port=${PORT:-$((RANDOM%10000+10000))}

run()
{
    echo $1
    if ! {
	    for j in $(seq 0 $2); do
		./$1-ecdsa-party.x -pn $port -p $j 1 2>logs/ecdsa-$j & true
	    done
	    wait
	} | tee logs/ecdsa | grep "Online checking"; then
	exit 1
    fi
}

for i in rep mal-rep shamir mal-shamir atlas sy-rep; do
    run $i 2
done

run rep4 3

for i in semi mascot; do
    run $i 1
done

./Fake-ECDSA.x
run fake-spdz 1
