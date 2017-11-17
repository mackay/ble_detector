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

format_datetime = function(utc_date_string) {
    return moment.utc(utc_date_string).local().format("YYYY-MM-DD HH:mm:ss");
};

format_ms_duration = function(duration) {
    var milliseconds = parseInt((duration%1000)/100, 10);
    var seconds = parseInt((duration/1000)%60, 10);
    var minutes = parseInt((duration/(1000*60))%60, 10);
    var hours = parseInt((duration/(1000*60*60))%24, 10);
    var days = parseInt((duration/(1000*60*60*24)), 10);

    hours = (hours < 10) ? "0" + hours : hours;
    minutes = (minutes < 10) ? "0" + minutes : minutes;
    seconds = (seconds < 10) ? "0" + seconds : seconds;

    if(days > 0) {
        return days + "d " + hours + "h " + minutes + "m";
    }

    if(hours > 0) {
        return hours + "h " + minutes + "m " + seconds + "s";
    }

    return minutes + "m " + seconds + "." + milliseconds + "s";
};

is_in_range = function(utc_date_string, range_seconds) {
    return moment.utc(utc_date_string).local() > moment().add(-1 * range_seconds, 'seconds');
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
    },

    get_beacons: function(callback) {
        this.get("/beacon", "", callback, this._general_failure);
    },
    get_detectors: function(callback) {
        this.get("/detector", "", callback, this._general_failure);
    },
    get_agents: function(callback) {
        this.get("/agent", "", callback, this._general_failure);
    },

    create_training_entry: function(beacon_uuid, expectation, callback) {
        this.post("/training", "", JSON.stringify({"beacon_uuid": beacon_uuid, "expectation": expectation}), callback, this._general_failure);
    }
});

ConfigManager = my.Class({
    constructor: function(api) {
        this.api = api;

        this.add_operation_hooks();
        this.add_reset_hooks();

        this.load();
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
            _.each( $(this).attr("resource").split(","), function(target_resource) {
                manager.api.del("/" + target_resource, "", function(data) {
                    toastr.success("Deleted {deleted} of resource type {resource}".format({
                        "deleted": data.deleted || 0,
                        "resource": target_resource }));
                }, manager.api._general_failure);
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

ViewManager = my.Class({

    constructor: function(api) {
        this.api = api;

        this.add_hooks();
        this.add_timer();

        this.load();
    },

    add_hooks: function() {
    },

    add_timer: function() {
        var manager = this;
        this.interval = setInterval(function() {
            if( $("#refresh:checked").length > 0 ) {
                manager.load();
            }
        }, 5000);
    },

    load: function() {
        this.load_beacons();
        this.load_detectors();
        this.load_agents();
    },

    load_beacons: function() {
        var manager = this;
        this.api.get_beacons(function(list) {
            var $tbody = $(".section.beacon table tbody");

            var template = _.template(
                    "<tr class='show-child-on-hover'>" +
                    "    <td>(<%- id %>) <%- uuid %> <div class='btn btn-xs btn-info btn-train hover-child' beacon='<%- uuid %>'>Create Training Entry</div></td>" +
                    "    <td><%- last_active %> <%= last_active_icon %></td>" +
                    "    <td><%- total_packets %></td>" +
                    "</tr>");

            $tbody.empty();
            _.each(list, function(item) {

                manager.add_html_status_icon(item, item.last_active);
                item.last_active = format_datetime(item.last_active);
                $tbody.append(template(item));
            });

            manager.add_beacon_hooks();
        });
    },
    add_beacon_hooks: function() {
        var manager = this;

        $(".btn-train").click(function() {
            var $btn = $(this);

            //if the button is disabled, don't do anything
            if($btn.hasClass("disabled")) {
                return;
            }

            //if the button is not disabled, disable and set a re-enable timer
            $btn.toggleClass("disabled", true);
            var timeout = setTimeout(function() {
                $btn.toggleClass("disabled", false);
                timeout = null;
            }, 1000);

            var beacon_uuid = $(this).attr("beacon");
            var expectation = JSON.parse( $("#training-data").val() );

            manager.api.create_training_entry(beacon_uuid, expectation, function() {
                toastr.success("Training entry created.");

                //if the re-enable timer didn't hit, re-enable here
                if(timeout) {
                    $btn.toggleClass("disabled", false);
                    clearTimeout(timeout);
                    timeout = null;
                }
            });
        });
    },

    load_detectors: function() {
        var manager = this;

        this.api.get_detectors(function(list) {
            var $tbody = $(".section.detector table tbody");

            var template = _.template(
                    "<tr>" +
                    "    <td>(<%- id %>) <%- uuid %></td>" +
                    "    <td><%- load %></td>" +
                    "    <td><%- last_active %> <%= last_active_icon %></td>" +
                    "    <td><%- total_packets %></td>" +
                    "</tr>");

            $tbody.empty();
            _.each(list, function(item) {
                item.load = "unknown";
                if( item.metadata && item.metadata.load ) {
                    item.load = item.metadata.load;
                }

                manager.add_html_status_icon(item, item.last_active);
                item.last_active = format_datetime(item.last_active);
                $tbody.append(template(item));
            });

            manager.add_detector_hooks();
        });
    },
    add_detector_hooks: function() {
    },

    load_agents: function() {

        var manager = this;

        this.api.get_agents(function(list) {
            var $tbody = $(".section.agent table tbody");

            var template = _.template(
                    "<tr>" +
                    "    <td>(<%- id %>) <%- uuid %></td>" +
                    "    <td><%- runtime %></td>" +
                    "    <td><%- last_active %> <%= last_active_icon %></td>" +
                    "    <td><%- sprite_count %></td>" +
                    "</tr>");

            $tbody.empty();
            _.each(list, function(item) {
                item.runtime = "unknown";
                item.sprite_count = "n/a";

                if( item.metadata ) {
                    if( item.metadata.runtime_ms ) {
                        item.runtime = format_ms_duration( parseFloat(item.metadata.runtime_ms) );
                    }

                    if( item.metadata.sprite_count ) {
                        item.sprite_count = item.metadata.sprite_count;
                    }
                }

                manager.add_html_status_icon(item, item.last_active);

                item.last_active = format_datetime(item.last_active);
                $tbody.append(template(item));
            });

            manager.add_agent_hooks();
        });
    },
    add_agent_hooks: function() {
    },

    add_html_status_icon: function(item, utc_date_string, range) {
        range = range || 5;

        if( is_in_range(item.last_active, range) ) {
            item.last_active_icon = this.html_good_icon();
        } else {
            item.last_active_icon = this.html_bad_icon();
        }
    },

    html_good_icon: function() {
        return '<span class="glyphicon glyphicon glyphicon-ok text-success" aria-hidden="true"></span>';
    },
    html_bad_icon: function() {
        return '<span class="glyphicon glyphicon glyphicon-remove text-danger" aria-hidden="true"></span>';
    }
});

environment = { };

$(function(){
    environment.service = new API("./api");
    environment.config = new ConfigManager( environment.service );


    environment.view = new ViewManager( environment.service );
});
