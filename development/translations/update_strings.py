#!/bin/bash
# This file must be executed from out of src
# This file replaces the english msgid in all files which contain it, 
# by the english msgstr (Useful when you have declared a string like 'strname' everywhere)
oldvalue=''
newvalue=''

file='preferences'

i=0

not_changed=""

# By default it will work on system deployed files
destination=/usr/share/slimbookbattery/

# Check if it is given an argument to translate repository instead of deployed files
if [ $# -ge 1 ] && [ $@[0] == "dev" } ]; then
	destination=$(pwd);
fi
echo "Replace will run in folder: $destination"

# 1. Busca los ids y msg del inglés
cd ./../../src/

echo $(pwd)"/tranlations/en/LC_MESSAGES/$file.po"

egrep 'msgid|msgstr' $(pwd)/translations/en/LC_MESSAGES/$file.po | while read -r line ; do
  
  
  if [ $((i%2)) -eq 0 ]; then # Si la linea es par (msgid)...
    #echo
    echo $line
    oldvalue=$(echo $line | grep -oP '\"\K[^"]+')	

  else # Si la linea es impar (msgid + msgstr)...
    echo $line
    newvalue=$(echo $line | grep -oP '\"\K[^"]+')
    
    #grep -rl "'$oldvalue'" . | xargs sed -i "'s/$oldvalue/$newvalue/g"

    cmd1="grep -rl '$oldvalue' $destination"
    #echo "$cmd1"


    # if [ $i -gt 2 ] && [ "$oldvalue" != "$newvalue" ]; then
      
    #   # Lets check that values don't contain special characters
    #   esc=true

    #   if echo "$oldvalue" | grep -q "/"; then
    #     #echo 'Found /'
    #     esc=false             
    #   fi
    #   if echo "$oldvalue" | grep -q "'"; then
    #     #echo "Found '"
    #     esc=false
    #   fi
    #   if $esc; then
    #     if echo "$newvalue" | grep -q "/"; then
    #     #echo 'Found /'
    #       esc=false               
    #     fi
    #     if echo "$newvalue" | grep -q "'"; then
    #       #echo "Found '"
    #       esc=false
    #     fi
    #   fi

    #   if $esc; then

    #     for file in $(eval $cmd1)
    #       do
    #         # $file: Aquí tenemos la ruta del archivo en el que se encuentra la palabra a reemplazar
    #         { # try
    #           #echo $file     
    #             echo \($oldvalue\) will be replaced by \($newvalue\)
    #             cmd2="sudo sed -i 's/$oldvalue/$newvalue/g' $file"
    #             { #try
    #               if eval $cmd2; then
    #                 echo 'Done'
    #               fi
      
    #             } || { #catch
    #               echo 'Check special chars'
    #             }
              
                    
    #         } || { # catch
            
    #           echo 'Not done'
    #           echo
    #         }

    #       done
    #     # else
    #     # echo "\033[0;31mCheck special chars $oldvalue \033[0m"
        
    #   fi
    # fi
  fi
  
  i=$((i + 1))
done
# echo "Not changed: $not_changed"




