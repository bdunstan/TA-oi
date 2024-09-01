 # Get the current dierctory of the script
SCRIPTS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -f "${SCRIPTS}/../setup.sh" ]
then
    source "${SCRIPTS}/../setup.sh"
fi

mkdir -p ${TA_OI}/${LOCATION} 2>/dev/null
cat /dev/null > ${TA_OI}/${LOCATION}/transforms.conf
 # Create a set of lookup files based on the contents of the API file
for QUERY in $( ls ${TA_OI}/kv_schema/ | egrep \.kv$ | sed s'/\.kv$//' )
do
    cat <<EOF >>${TA_OI}/${LOCATION}/transforms.conf
[${COLLECTION_PREFIX}${QUERY,,}]
batch_index_query = 0
case_sensitive_match = 0
filename = ${LOOKUP_FILE_PREFIX}${QUERY,,}.csv

EOF

    cat <<EOF >>${TA_OI}/${LOCATION}/transforms.conf
[${QUERY,,}]
batch_index_query = 0
case_sensitive_match = 0
filename = ${QUERY,,}.csv

EOF
    
    FIELD_LIST=$(cat ${TA_OI}/kv_schema/${QUERY}.kv | grep -v "^\s+$" | grep -v "^\s+#" | head -n 1)
    cat <<EOF >>${TA_OI}/${LOCATION}/transforms.conf
[kv_${COLLECTION_PREFIX}${QUERY,,}]
external_type = kvstore
collection = ${COLLECTION_PREFIX}${QUERY,,}
fields_list = _key, ${FIELD_LIST}
disabled = 0

EOF

done

 # Force the sourcetype to change based on the input - this is if we are indexing the data not just 
 # using lookups
 cat <<EOF >>${TA_OI}/${LOCATION}/transforms.conf
[force-oi-sourcetype]
DEST_KEY = MetaData:Sourcetype
SOURCE_KEY = MetaData:Source
# Directory structure
# .../data/<sourcetype>.json
REGEX = \/\w+\/(\w+)\.(?:\d+\.)?(?:json|gz|jsonl)\$
FORMAT = sourcetype::cisco:bcs:\$1
WRITE_META = true

[force-oi-host]
DEST_KEY = MetaData:Host
SOURCE_KEY = MetaData:Source
# Directory structure
# .../data/<host>/sourcetype.json
REGEX = \/(\w+)\/\w+\.(?:\d+\.)?(?:json|gz|jsonl)$
FORMAT = host::\$1
WRITE_META = true

EOF
