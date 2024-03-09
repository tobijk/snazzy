BOLT_ENVIRONMENT_SH_PRE_FLIGHT_CHECKS_OK=true

if [ ! -f "environment.sh" ]; then
    echo "The environment.sh file must be sourced locally as '. ./environment.sh'."
    BOLT_ENVIRONMENT_SH_PRE_FLIGHT_CHECKS_OK=false
fi

if [ "$BOLT_ENVIRONMENT_SH_PRE_FLIGHT_CHECKS_OK" = true ]; then
    if [ "x$BOLT_LOCAL_PROJECT_SOURCED" = "x" ]; then
        PYTHONPATH="$(pwd)/lib:$PYTHONPATH"
        PATH="$(pwd)/bin:$PATH"

        export PATH
        export PYTHONPATH
        export PS1="(snazzy)$PS1"
        export BOLT_LOCAL_PROJECT_SOURCED="yes"
    fi
fi

unset BOLT_ENVIRONMENT_SH_PRE_FLIGHT_CHECKS_OK
