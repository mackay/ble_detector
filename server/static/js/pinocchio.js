
//first we need to create the base class for the security credential object(s)
extend('pinocchio.security',{

    //SecurityCredential: a base object to handle injecting security into any
    //   service class as well as holding general info for the current session
    SecurityCredential: my.Class({

        constructor: function( user_uri, first_name, last_name ) {
            this.update_user( user_uri, first_name, last_name );
            this.update_session( null, null );
        },

        update_user: function( user_uri, first_name, last_name ) {
            this.first_name = first_name || "unknown";
            this.last_name = last_name || "unknown";
            this.user_uri = user_uri || "/user/none";
        },

        update_session: function( token, date ) {
            this.token = token;
            this.date = date;
        },


        //the following functions are for detailed security data for session headers
        get_user: function() {
            return this.user_uri;
        },

        get_token: function() {
            return this.token;
        },

        get_auth_date: function() {
            return this.date;
        },

        security_headers: function() {

            var headers = { };

            headers["x-pinocchio-token"] = this.get_token();
            headers["x-pinocchio-date"] = this.get_auth_date();
            headers["x-pinocchio-user"] = this.get_user();

            return headers;
        }
    })
});

//second we can create the specialized classes for security
extend('pinocchio.security',{

    //Basic Auth: typical basic auth headers added to each call
    BasicAuthSecurity: my.Class(pinocchio.security.SecurityCredential, {

        constructor: function(user, pass) {
            pinocchio.security.BasicAuthSecurity.Super.call(this);
        },

        set_user: function( user ) {

        },
        set_pass: function( pass ) {

        },

        security_headers: function() {
            headers = pinocchio.security.BasicAuthSecurity.Super(this);
            headers["Authorization"] = "<<tbd base 64 encoding of above data>>";
            return { };
        }
    }),

    //Cookie Security: a security mechanism example that uses/creates/validates
    //  a proper cookie for authentication use in the service calls
    CookieSecurity: my.Class(pinocchio.security.SecurityCredential, {

        constructor: function() {
            pinocchio.security.CookieSecurity.Super.call(this);

            //TBD: create example cookie-based security handler
        }
    }),

    //Passive Security: we don't add a thing and let somethign else handle sec
    PassiveSecurity: my.Class(pinocchio.security.SecurityCredential, {

        constructor: function() {
            pinocchio.security.PassiveSecurity.Super.call(this);
        },

        //make sure we don't add a single header
        security_headers: function() {
            return { };
        }
    }),
});

extend('pinocchio.util', {

    get_expansion: function( uri, base, field ) {

        field = field || "url";

        for(var i=0; i<base.length; i++) {

            if( base[i][field] == uri ) {
                return base[i];
            }
        }

        return { };
    }
});

extend('pinocchio', {

    EVENT: {
        INIT: "/pinocchio/init"
    },

    View: my.Class({

        display_css_type: "block",

        id: null,
        selector: null,
        model: null,
        update_on_model_change: false,
        render_on_model_change: false,
        hidden: true,

        last_model_tag: 0,

        constructor: function( id, selector, model, update_on_change, render_on_change, start_hidden ) {

            this.id = id;
            this.selector = selector;
            this.model = model;
            this.update_on_model_change = update_on_change;
            this.render_on_model_change = render_on_change;

            this.hidden = start_hidden || true;

            if( typeof model != 'undefined' && model.id !== null && this.update_on_model_change ) {
                radio( model.change_event_path() ).subscribe([this.update, this]);
            }
        },
        show: function() {
            $(this.selector).css("display", this.display_css_type);
            this.hidden = false;
        },
        hide: function() {
            $(this.selector).css("display", "none");
            this.hidden = true;
        },
        update: function() {
            //overriding functions should perform **any**!!
            //   actions necessary **BEFORE** calling Super on this guy
            //
            //   and because my.Class can get confusing, you call it like...
            //
            //  pinocchio.mock.View.Super.prototype.update.call(this);

            if( this.render_on_model_change && this.model.tag != this.last_model_tag ) {
                this.last_model_tag = this.model.tag;


                if(!this.hidden) {
                    console.log("Rendering " + this.id);
                    this.render();
                } else {
                    //console.log("Not rendering " + this.id + ", view is hidden.");
                }
            }
        },
        render: function() {
            //this is just a placeholder for a super class to override
        }
    }),

    Model: my.Class({

        tag: null,
        id: null,

        constructor: function( id ) {
            this.id = id;
            this.tag = 0;

            //this.changed = _.debounce(this.changed, 100);
            //this.changed = _.debounce(this.changed, 25);

            this._send_event = _.debounce(this._send_event, 100);
            this.do_change = true;
        },
        changed: function() {
            if( !this.do_change ) {
                return;
            }

            var d = new Date();
            this.tag = murmurhash3_32_gc( d.valueOf().toString() );

            this._send_event();
        },
        change_event_path: function() {
            return "/pinocchio/model/" + this.id + "/changed";
        },
        _send_event: function() {
            radio(this.change_event_path()).broadcast(this);
            $(this).trigger("model_changed", this);
        },

        disable_change_event: function() {
            this.do_change = false;
            return this;
        },
        enable_change_event: function() {
            this.do_change = true;
            return this;
        }
    }),

    App: my.Class({
        name: null,
        security: new pinocchio.security.PassiveSecurity(),
        services: { },
        views: { },
        models: { },

        constructor: function( name, security, services ) {
            radio( pinocchio.EVENT.INIT ).subscribe([this.init, this]);

            this.name = name;
            this.security = security;

            for( var service_key in services ) {
                this.services[service_key] = services[service_key];
            }
        },
        init: function() {
            //super classes init "stuff" here
        },


        get_service: function( id ) {
            if( !this.services.hasOwnProperty(id) ) {
                throw("No service available with id " + id + ".");
            }

            return this.services[id];
        },

        add_view: function( view, add_model, replace_existing ) {
            add_model = add_model || false;
            replace_existing = replace_existing || false;

            if( this.views.hasOwnProperty(view.id) && !replace_existing ) {
                throw("Already have view " + view.id + " in the application.");
            }
            this.views[view.id] = view;

            if( add_model ) {
                this.add_model( view.model, replace_existing );
            }

            return this;
        },
        get_view: function( id ) {
            if( !this.views.hasOwnProperty(id) ) {
                throw("No view with id " + id + " in the application.");
            }

            return this.views[id];
        },
        hide_view: function( id ) {
            if( typeof id != "undefined" && id !== null ) {
                this.get_view(id).hide();
            } else {
                for( var view_id in this.views ) {
                    this.views[view_id].hide();
                }
            }
        },
        show_view: function( id ) {
            this.get_view(id).show();
        },
        show_only: function( id ) {
            this.hide_view();
            this.show_view( id );
        },

        add_model: function( model, replace_existing ) {
            replace_existing = replace_existing || false;

            if( this.models.hasOwnProperty(model.id) && !replace_existing ) {
                throw("Already have model " + model.id + " in the application.");
            }

            this.models[model.id] = model;
            return this;
        },
        get_model: function( id ) {
            if( !this.models.hasOwnProperty(id) ) {
                throw("No model with id " + id + " in the application.");
            }

            return this.models[id];
        }
    }),


    //build out the base class for all service calls, really just a wrapper for
    //   jquery ajax calls using the above credential classes with some syntactic
    //   preference for how the calls can be employed
    Service: my.Class({

        STATIC: {
            build_url: function( base, uri, query ) {
                var url = base + uri;

                if( query && query.length > 0 ) {
                    url = url + "?" + query;
                }

                return url;
            }
        },

        constructor: function( base_url, security_credentials ) {
            this.base = base_url;
            this.credentials = security_credentials;
        },

        get_cached: function(uri, query, success, failure, headers) {
            $.ajax({
                type: "GET",
                contentType: "application/json",
                url: pinocchio.Service.build_url( this.base, uri, this._query(query)),
                success: this._success( success ),
                error:   this._error( failure ),
                headers: this._headers( headers ),
                cache:   true
            });
        },

        get: function(uri, query, success, failure, headers) {
            $.ajax({
                type: "GET",
                contentType: "application/json",
                url: pinocchio.Service.build_url( this.base, uri, this._query(query)),
                success: this._success( success ),
                error:   this._error( failure ),
                headers: this._headers( headers )
            });
        },

        post: function(uri, query, body, success, failure, headers) {
            $.ajax({
                type: "POST",
                contentType: "application/json",
                data: body,
                dataType: "json",
                url: pinocchio.Service.build_url( this.base, uri, this._query(query)),
                success: this._success( success ),
                error:   this._error( failure ),
                headers: this._headers( headers )
            });
        },

        put: function(uri, query, body, success, failure, headers) {
            $.ajax({
                type: "PUT",
                contentType: "application/json",
                data: body,
                dataType: "json",
                url: pinocchio.Service.build_url( this.base, uri, this._query(query)),
                success: this._success( success ),
                error:   this._error( failure ),
                headers: this._headers( headers )
            });
        },

        patch: function(uri, query, body, success, failure, headers) {
            $.ajax({
                type: "PATCH",
                contentType: "application/json",
                data: body,
                dataType: "json",
                url: pinocchio.Service.build_url( this.base, uri, this._query(query)),
                success: this._success( success ),
                error:   this._error( failure ),
                headers: this._headers( headers )
            });
        },

        del: function(uri, query, success, failure, headers) {
            $.ajax({
                type: "DELETE",
                contentType: "application/json",
                url: pinocchio.Service.build_url( this.base, uri, this._query(query)),
                success: this._success( success ),
                error:   this._error( failure ),
                headers: this._headers( headers )
            });
        },

        delb: function(uri, query, body, success, failure, headers) {
            $.ajax({
                type: "DELETE",
                contentType: "application/json",
                data: body,
                dataType: "json",
                url: pinocchio.Service.build_url( this.base, uri, this._query(query)),
                success: this._success( success ),
                error:   this._error( failure ),
                headers: this._headers( headers )
            });
        },

        _query: function( user_query ) {
            return user_query;
        },

        _headers: function( supplemental_headers ) {

            supplemental_headers = supplemental_headers || { };
            headers = this.credentials.security_headers();

            for(var key in supplemental_headers) {
                headers[key] = supplemental_headers[key];
            }

            return headers;
        },

        _error: function( callback ) {
            return function(error, status) {
                callback = callback || function() { };
                callback( error, status );
            };
        },

        _success: function( callback ) {
            return function(data, status) {
                callback = callback || function() { };
                callback(data, status);
            };
        }
    })
});

extend('pinocchio', {
    Mixin: my.Class({

        mixins: [ ],
        base: null,

        constructor: function( target_object ) {
            this.base = target_object;
            this.mix();
        },
        mix: function( bind_target ) {

            var target = this.base;
            var source = this;

            bind_target = bind_target || this;

            var method;
            var length = this.mixins.length;
            for(var i = 0; i < length; i++){
                method = this.mixins[i];

                // bind the function from the source and assign the
                // bound function to the target
                target[method] = _.bind(source[method], bind_target);
            }
        }
    })
});




