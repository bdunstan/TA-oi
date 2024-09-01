#!env bash

# Get the current directory of the script
SCRIPTS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

 # Setup the environment
if [ -f "${SCRIPTS}/../setup.sh" ]
then
    source ${SCRIPTS}/../setup.sh
fi

 # Create the props (sourcetypes)
bash ${SCRIPTS}/create_props.bash
 
 # Create the kvstore collections 
bash ${SCRIPTS}/create_collections.bash

 # Create the searches used to populate the kvstore 
bash ${SCRIPTS}/create_collection_searches.bash

 # Create the transforms - rewrite sourcetype and lookup/kv definitions
bash ${SCRIPTS}/create_transforms.bash

 # Create the inputs - if you want to index data
## Although this is created, its disabled by default
# bash ${SCRIPTS}/create_inputs.bash

 # Create the indexes - if you want to index data
# Disabled 17 Jun 22 - hand over index creation to the Adminstrator.
# bash ${SCRIPTS}/create_index.bash