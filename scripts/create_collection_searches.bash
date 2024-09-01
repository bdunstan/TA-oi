 # Get the current dierctory of the script
SCRIPTS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -f "${SCRIPTS}/../setup.sh" ]
then
    source "${SCRIPTS}/../setup.sh"
fi

mkdir -p ${TA_OI}/searches 2>/dev/null
 # Clean our the old collections file
cat /dev/null > ${TA_OI}/searches/collection_searches.txt
cat /dev/null > ${TA_OI}/${LOCATION}/savedsearches.conf

 # Create a set of collections based on the contents of the API file
for QUERY in $( ls ${TA_OI}/kv_schema/ | egrep \.kv$ | sed s'/\.kv$//' )
do
    cat <<EOF >>${TA_OI}/searches/collection_searches.txt
| inputlookup ${LOOKUP_FILE_PREFIX}${QUERY,,}.csv | outputlookup kv_${COLLECTION_PREFIX}${QUERY,,}
EOF

    cat <<EOF >>${TA_OI}/${LOCATION}/savedsearches.conf
[populate_kv_${QUERY,,}]
action.email.useNSSubject = 1
alert.track = 0
description = Populate the kvstore for ${QUERY,,}
cron_schedule = 15 1 * * *
enableSched = 1
search = | inputlookup ${LOOKUP_FILE_PREFIX}${QUERY,,}.csv | outputlookup kv_${COLLECTION_PREFIX}${QUERY,,}

EOF
done
