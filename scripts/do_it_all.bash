#!env bash

# Get the current directory of the script
SCRIPTS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

 # Setup the environment
if [ -f "${SCRIPTS}/../setup.sh" ]
then
    source ${SCRIPTS}/../setup.sh
fi

echo "${SCRIPTS}/get_alerts.bash"
 # Get the latest bulk data from the API
bash ${SCRIPTS}/get_alerts.bash

 # Create the lookups and json files for indexing
echo "${SCRIPTS}/api2splunk.bash"
bash ${SCRIPTS}/api2splunk.bash

 # Create the ALEX module, this uses the oi-class.py logic to identify what class a device belongs to.
 echo "bash ${SCRIPTS}/api2alex.bash"
bash ${SCRIPTS}/api2alex.bash

 # Create the transforms - basically add the lookup definitions
 echo "bash ${SCRIPTS}/create_transforms.bash"
bash ${SCRIPTS}/create_transforms.bash

# Sleep 600 - need to manage this better to give splunk time to ingest the data - and/or run this on regular basis
 # Populate the kvstore with data we have ingested
 echo "sleep"
sleep 600
echo "bash ${SCRIPTS}/populate_collections.bash"
bash ${SCRIPTS}/populate_collections.bash
