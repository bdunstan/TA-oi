if [ -z ${TA_OI} ]
then
  export TA_OI="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
fi

if [ -f ~/.env ]
then
  source ~/.env
fi

 # Setup any environment variables, like tokens, keys etc...
if [ -f ${TA_OI}/.env ]
then
  source ${TA_OI}/.env
fi

export APP_NAME="TA-oi"
export API_DATA="${TA_OI}/api_data"
export DATA="${TA_OI}/data"
export BIN="${TA_OI}/bin"
export YMD=`date '+%Y%m%d'`
export DATE=`date '+%Y%m%d%H%M%S'`
export TIMESTAMP=`date '+%Y-%m-%dT%H:%M:%S'`

export LOCATION="default"

export PYTHON3=$( which python3 )
export PYTHON=$( which python3 )

export COLLECTION_PREFIX="cisco:bcs:"
export LOOKUP_FILE_PREFIX="cisco_bcs-"


case "$OSTYPE" in
  linux*)   source ${TA_OI}/setup-linux.sh ;;
  darwin*)  source ${TA_OI}/setup-darwin.sh ;; 
  bsd*)     echo "BSD" ;;
  *)        echo "unknown: $OSTYPE" ;;
esac
