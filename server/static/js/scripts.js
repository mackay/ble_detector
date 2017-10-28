

API = my.Class(pinocchio.Service, {
    constructor: function(base_url) {
        API.Super.call(this, base_url, new pinocchio.security.PassiveSecurity() );
    },

    _general_failure: function(a,b,c) {
        toastr.error("API failure");
    },

    set_option: function(key, value, callback) {
        this.post("/option", "", JSON.stringify({"key": key, "value": value}), callback, this._general_failure);
    },
    get_options: function(callback) {
        this.get("/option", "", callback, this._general_failure);
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

        $("#filter-data").change(function(){
            manager.api.set_option("filter-data", $(this).val(), function() {
                toastr.success("Filter Set");
            });
        });
    },

    load: function() {
        this.api.get_options(function(data) {
            $("#mode option[value='" + data["mode"] + "']").prop("selected", true);
            $("#training-data").val(data["training-data"]);
            $("#filter-data").val(data["filter-data"]);
        });
    }
});

environment = { };

$(function(){
    environment.service = new API("./api");
    environment.config = new ConfigManager( environment.service );

    environment.config.add_hooks();
    environment.config.load();
});
