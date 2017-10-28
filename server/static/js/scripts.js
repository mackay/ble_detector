/**
 * Sprintf like function
 * @source http://stackoverflow.com/a/4795914/805649
 * @return String
 */
String.prototype.format = function() {
    "use strict";

    var formatted = this;
    for (var prop in arguments[0]) {
        if (arguments[0].hasOwnProperty(prop)) {
            var regexp = new RegExp("\\{" + prop + "\\}", "gi");
            formatted = formatted.replace(regexp, arguments[0][prop]);
        }
    }
    return formatted;
};


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

    add_operation_hooks: function() {
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

    add_reset_hooks: function() {
        var manager = this;

        $(".reset .btn").click(function() {
            var target_resource = "/" + $(this).attr("resource");
            manager.api.del(target_resource, "", function(data) {
                toastr.success("Deleted {deleted} of resource type {resource}".format({
                    "deleted": data.deleted || 0,
                    "resource": target_resource }));
            }, manager.api._general_failure);
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

    environment.config.add_operation_hooks();
    environment.config.add_reset_hooks();

    environment.config.load();
});
