#!/bin/bash

#TIME_BETWEEN=$(cat /sys/class/power_supply/BAT0/uevent | grep -i capacity | cut -d'=' -f2)

user=$(last -wn1 | head -n 1 | cut -f 1 -d " ")
home=$(cat /etc/passwd | grep "$user" | cut -d":" -f6)



MAX_BAT=$(cat $home/.config/slimbookbattery/slimbookbattery.conf | grep 'max_battery_value' | cut -d'=' -f2)

MIN_BAT=$(cat $home/.config/slimbookbattery/slimbookbattery.conf | grep 'min_battery_value' | cut -d'=' -f2)

TIME_BETWEEN=$(cat $home/.config/slimbookbattery/slimbookbattery.conf | grep 'time_between_warnings' | cut -d'=' -f2)

TIMES=$(cat $home/.config/slimbookbattery/slimbookbattery.conf | grep 'max_battery_times' | cut -d'=' -f2)

last_value=-1

echo "User: $user"
echo "Max battery alert at: $MAX_BAT%"
echo "Min battery alert at: $MIN_BAT%"
echo "Time between alerts: $TIME_BETWEEN s"
echo "Repeat alerts: $TIMES times"

# Check if the battery is connected
if [ -e /sys/class/power_supply/BAT0 ]; then

    while true;do   
		# Get the capacity
		CAPACITY=$(cat /sys/class/power_supply/BAT0/capacity)
	    
		#if we are reading at the same capacity value; pass
		if [ $last_value -ne $CAPACITY ]; then
			
			echo "Actual capacity: $CAPACITY%"

				STATUS=$( cat /sys/class/power_supply/BAT0/status )
			
			if [ $STATUS == "Charging" ] && [ $CAPACITY == $MAX_BAT ]; then

				for (( i=1; i<=$TIMES; i++ ))
				do  
				echo 'Notification sent'
				su $user -c 'notify-send --icon=/usr/share/slimbookbattery/images/normal.png "Battery is quite full charged!" "Actual value $(cat /sys/class/power_supply/BAT0/capacity) %"'
				sleep $TIME_BETWEEN
				done

			fi
			
			if [ $STATUS == "Discharging" ] && [ $CAPACITY == $MIN_BAT ]; then

				for (( i=1; i<=$TIMES; i++ ))
				do  
				echo 'Notification sent'
				su $user -c 'notify-send --icon=/usr/share/slimbookbattery/images/normal.png "Battery is low, connect your charger!" "Actual value $(cat /sys/class/power_supply/BAT0/capacity) %"'
				sleep $TIME_BETWEEN
				done

			fi
		fi		

	    #Sleeping to read if value changed
		last_value=$CAPACITY
		#echo "Last value: $last_value"
	    	sleep 45
    done
fi
exit 0