 # Get the current dierctory of the script
SCRIPTS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -f "${SCRIPTS}/../setup.sh" ]
then
    source "${SCRIPTS}/../setup.sh"
fi

mkdir -p ${TA_OI}/${LOCATION} 2>/dev/null
 # Clean our the old collections file
cat /dev/null > ${TA_OI}/${LOCATION}/collections.conf

 # Create a set of collection  based on the contents of the API file
for QUERY in $( ls ${TA_OI}/kv_schema/ | egrep \.kv$ | sed s'/\.kv$//' )
do
    echo "[${COLLECTION_PREFIX}${QUERY,,}]" >>${TA_OI}/${LOCATION}/collections.conf

    for FIELD in $( cat "${TA_OI}/kv_schema/${QUERY}.kv" | tr -s "," "\n" )
    do
        echo "field.${FIELD} = string" >>${TA_OI}/${LOCATION}/collections.conf
    done
    echo "" >>${TA_OI}/${LOCATION}/collections.conf

done
