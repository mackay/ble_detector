

API = my.Class(pinocchio.Service, {
    constructor: function(base_url) {
        API.Super.call(this, base_url, new pinocchio.security.PassiveSecurity() );
    },

    _general_failure: function(a,b,c) {
        toastr.error("API failure");
    },

    set_option: function(key, value, callback) {
        this.post("/option", "", JSON.stringify({"key": key, "value": value}), callback, this._general_failure);
    }
});


ConfigManager = my.Class({
    constructor: function(api) {
        this.api = api;
    },

    add_hooks: function() {
        var manager = this;

        $("#mode").change(function(){
            manager.api.set_option("mode", $(this).val(), function() {
                toastr.success("Mode Set");
            });
        });

        $("#training-data").change(function(){
            manager.api.set_option("training-data", $(this).val(), function() {
                toastr.success("Training Mode");
            });
        });

        $("#beacon-filter-data").change(function(){
            manager.api.set_option("filter-data", $(this).val(), function() {
                toastr.success("Filter Set");
            });
        });
    }
});

environment = { };

$(function(){
    environment.service = new API("./api");
    environment.config = new ConfigManager( environment.service );

    environment.config.add_hooks();
});
