odoo.define('solse_multi_branch.SessionNew', function(require) {
"use strict";

/**
 * When Odoo is configured in multi-branch mode, users should obviously be able
 * to switch their interface from one branch to the other.  This is the purpose
 * of this widget, by displaying a dropdown menu in the systray.
 */

var config = require('web.config');
var core = require('web.core');
var new_session = require('web.Session');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var mixins = require('web.mixins');
var utils = require('web.utils');
var _t = core._t;

var SucursalSession = new_session.include({
    setSucursales: function (main_branch_id, branch_ids) {
        var hash = $.bbq.getState()
        hash.bids = branch_ids.sort(function(a, b) {
            if (a === main_branch_id) {
                return -1;
            } else if (b === main_branch_id) {
                return 1;
            } else {
                return a - b;
            }
        }).join(',');
        utils.set_cookie('bids', hash.bids || String(main_branch_id));
        $.bbq.pushState({'bids': hash.bids}, 0);
        location.reload();
    },
});
})
