from bottle import request, abort


def require_fields( field_list ):
    def require_fields_wrapper( func ):
        def require_fields_chain_fn(*args, **kwargs):

            if any(field not in request.json for field in field_list):
                message = "Missing required field in body.\n\nFields expected: {expected}\n\nFields supplied: {supplied}".format(
                    expected=str(field_list),
                    supplied=str(request.json.keys()) )

                abort(400, message)
            return func( *args, **kwargs )

        return require_fields_chain_fn
    return require_fields_wrapper
