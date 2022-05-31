odoo.define('solse_multi_branch.SwitchCompanyMenu', function(require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var session = require('web.session');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var mixins = require('web.mixins');
var utils = require('web.utils');
var SwitchCompanyMenu = require('web.SwitchCompanyMenu');
var _t = core._t;

SwitchCompanyMenu.include({
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onSwitchCompanyClick: function (ev) {
        var res = this._super.apply(this, arguments);
        ev.stopPropagation();
        var dropdownItem = $(ev.currentTarget).parent();
        var cmpID = dropdownItem.data('company-id');
        var brh_id = this.get_curr_cmp_branch(cmpID);
        if(brh_id){ this.switch_company_branch(brh_id[0], brh_id[1]); }
        return res;
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onToggleCompanyClick: function (ev) {
        var res = this._super.apply(this, arguments);
        var allowed_company_ids = this.allowed_company_ids;
        var current_company_id = allowed_company_ids[0];
        ev.stopPropagation();
        var dropdownItem = $(ev.currentTarget).parent();
        var cmpID = current_company_id;
        var brh_id = this.get_curr_cmp_branch(cmpID);
        if(brh_id){ this.switch_company_branch(brh_id[0], brh_id[1]); }
        return res;
    },

    get_curr_cmp_branch: function(cmpID) {
        for (var i=0; i<session.user_branches.allowed_branches.length; i++) {
            if (session.user_branches.allowed_branches[i][2] == cmpID) {
                return session.user_branches.allowed_branches[i];
            }
        }
        return false;
    },

    switch_company_branch: function(brh_id, branch_name) {
        var self = this;
        session.user_branches.current_branch[0] = brh_id;
        session.user_branches.current_branch[1] = branch_name;
        $('.o_switch_branch_menu .oe_topbar_name').text(session.user_branches.current_branch[1]);
        session.user_context.allowed_branch_ids = [brh_id];
        this.allowed_branch_ids = String(session.user_context.allowed_branch_ids)
                                    .split(',')
                                    .map(function (id) {return parseInt(id);});
        this.user_branches = session.user_branches.allowed_branches;
        this.current_branch = brh_id;
        this.current_branch_name = _.find(session.user_branches.allowed_branches, function (branch) {
            return branch[0] === self.current_branch;
        })[1];
        session.setSucursales(brh_id, this.allowed_branch_ids);
	}
});
});
