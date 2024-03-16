SNAZZY_ENVIRONMENT_SH_PRE_FLIGHT_CHECKS_OK=true

if [ ! -f "environment.sh" ]; then
    echo "The environment.sh file must be sourced locally as '. ./environment.sh'."
    SNAZZY_ENVIRONMENT_SH_PRE_FLIGHT_CHECKS_OK=false
fi

if [ "$SNAZZY_ENVIRONMENT_SH_PRE_FLIGHT_CHECKS_OK" = true ]; then
    if [ "x$SNAZZY_LOCAL_PROJECT_SOURCED" = "x" ]; then
        PYTHONPATH="$(pwd)/lib:$PYTHONPATH"
        PATH="$(pwd)/bin:$PATH"

        export PATH
        export PYTHONPATH
        export PS1="(snazzy)$PS1"
        export SNAZZY_LOCAL_PROJECT_SOURCED="yes"
    fi
fi

unset SNAZZY_ENVIRONMENT_SH_PRE_FLIGHT_CHECKS_OK
