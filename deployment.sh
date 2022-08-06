FILE=deployment.zip
if test -f "$FILE"; then
    rm $FILE 
fi
cd warframeMarket/lib/python3.9/
zip -r ../../../$FILE .
cd ../../..
zip -g $FILE  warframeNotift.py