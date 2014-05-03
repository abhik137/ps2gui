#/bin/bash


which xdotool 1>/dev/null || { echo "Please install xdotool"; exit; }

windownum=$(xdotool search --name "bits-pilani")
xdotool windowfocus $windownum

for i in {0..7}
do
xdotool key Tab
done


while read line
do
pref=$(echo $line | awk '{print $2}')
xdotool type $pref
xdotool key Tab
done<"$HOME/finalpreflist"

## Fail safe
for i in {0..2}
do
xdotool key Tab
done

echo "The code has been executed. Give the page a few seconds to reflect the changes"
echo "Please ****vertify**** the list and only then submit"
