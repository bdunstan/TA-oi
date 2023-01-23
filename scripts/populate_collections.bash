 # Get the current dierctory of the script
SCRIPTS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -f "${SCRIPTS}/../setup.sh" ]
then
    source "${SCRIPTS}/../setup.sh"
fi

URI="servicesNS/-/-/search/jobs/export"
while IFS= read -r line
do
    
    echo "curl -s -ku \"${SPLUNK_USERNAME}:${SPLUNK_PASSWORD}\" \"https://localhost:8089/${URI}\" --data-urlencode search=\"${line}\" "
    curl -s -ku "${SPLUNK_USERNAME}:${SPLUNK_PASSWORD}" "https://localhost:8089/${URI}" --data-urlencode search="${line}"  > ${TA_OI}/logs/populate_collections

done <${TA_OI}/searches/collection_searches.txt