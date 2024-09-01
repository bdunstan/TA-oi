 # Get the current dierctory of the script
SCRIPTS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -f "${SCRIPTS}/../setup.sh" ]
then
    source "${SCRIPTS}/../setup.sh"
fi

mkdir -p ${TA_OI}/${LOCATION} 2>/dev/null
cat /dev/null > ${TA_OI}/${LOCATION}/indexes.conf

 cat <<EOF >>${TA_OI}/${LOCATION}/indexes.conf
[oi]
coldPath = \$SPLUNK_DB/oi/colddb
homePath = \$SPLUNK_DB/oi/db
maxTotalDataSizeMB = 30720
thawedPath = \$SPLUNK_DB/oi/thaweddb
compressRawdata = 1
enableDataIntegrityControl = 0
disabled = 1

EOF