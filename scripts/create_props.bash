 # Get the current dierctory of the script
SCRIPTS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -f "${SCRIPTS}/../setup.sh" ]
then
    source "${SCRIPTS}/../setup.sh"
fi

mkdir -p ${TA_OI}/${LOCATION} 2>/dev/null
cat /dev/null > ${TA_OI}/${LOCATION}/props.conf
 # Create a set of lookup files based on the contents of the API file
cat <<EOF >>${TA_OI}/${LOCATION}/props.conf

[source::.../${APP_NAME}/data/*/*.gz]
KV_MODE = none
INDEXED_EXTRACTIONS = json

[source::.../${APP_NAME}/data/*/*.json]
KV_MODE = none
INDEXED_EXTRACTIONS = json

[source::.../${APP_NAME}/data/*/*.jsonl]
KV_MODE = none
INDEXED_EXTRACTIONS = json

[oi]
pulldown_type = true
category = Structured
description = JavaScript Object Notation format. For more information, visit http://json.org/
TIMESTAMP_FIELDS = timeStamp,timestamp
TRANSFORMS-fs = force-oi-sourcetype
TRANSFORMS-fh = force-oi-host
KV_MODE = none
INDEXED_EXTRACTIONS = json
TRUNCATE = 0

EOF
