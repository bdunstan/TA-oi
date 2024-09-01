 # Get the current dierctory of the script
SCRIPTS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -f "${SCRIPTS}/../setup.sh" ]
then
    source "${SCRIPTS}/../setup.sh"
fi

mkdir -p ${TA_OI}/${LOCATION} 2>/dev/null
cat /dev/null > ${TA_OI}/${LOCATION}/inputs.conf

path_length=${TA_OI//[!\/]}

 cat <<EOF >>${TA_OI}/${LOCATION}/inputs.conf
[monitor://${TA_OI}/data]
disabled = true
host_segment = $((${#path_length}+2))
index = oi
recursive = 1
sourcetype = oi
whitelist = \.(json|jsonl|gz)$

EOF