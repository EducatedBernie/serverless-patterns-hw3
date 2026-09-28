#!/bin/bash
url=$1
TOKEN=$2
AUTH_HEADER="Authorization:$TOKEN"
interval_in_seconds=2
result="1024"
printf "\nPolling '$url' every $interval_in_seconds seconds, until '$result'\n"
while true; 
do 
	x=$(curl $url -H "$AUTH_HEADER"); 
	printf "\r$(date +%H:%M:%S): $x";
	if [[ "$x" == "$result" ]]; then 
		break; 
	fi; 
	sleep $interval_in_seconds; 
done

