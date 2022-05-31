odoo.define('solse_multi_branch.AbstractWebClient', function (require) {
"use strict";

var AbstractWebClient = require('web.AbstractWebClient');
var session = require('web.session');
var utils = require('web.utils');

AbstractWebClient.include({
    start: function () {
        var self = this;
        var state = $.bbq.getState();
        var current_branch_id = session.user_branches.current_branch[0]
        if (!state.bids) {
            state.bids = utils.get_cookie('bids') !== null ? utils.get_cookie('bids') : String(current_branch_id);
        }
        var stateSucursalIDS = _.map(state.bids.split(','), function (bid) { return parseInt(bid) });
        var userSucursalIDS = _.map(session.user_branches.allowed_branches, function(branch) {return branch[0]});
        if (!_.isEmpty(_.difference(stateSucursalIDS, userSucursalIDS))) {
            state.bids = String(current_branch_id);
            stateSucursalIDS = [current_branch_id]
        }
        session.user_context.allowed_branch_ids = stateSucursalIDS;
        $.bbq.pushState(state);
        return this._super.apply(this, arguments);
    },
});
});
