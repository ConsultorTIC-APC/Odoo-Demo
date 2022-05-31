odoo.define('solse_multi_branch.SwitchSucursalMenu', function(require) {
"use strict";

/**
 * When Odoo is configured in multi-branch mode, users should obviously be able
 * to switch their interface from one branch to the other.  This is the purpose
 * of this widget, by displaying a dropdown menu in the systray.
 */

var config = require('web.config');
var core = require('web.core');
var session = require('web.session');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var mixins = require('web.mixins');
var utils = require('web.utils');
var _t = core._t;

var SwitchSucursalMenu = Widget.extend({
    template: 'SwitchSucursalMenu',
    events: {
        'click .dropdown-item[data-menu] div.log_into': '_onSwitchSucursalClick',
        'click .dropdown-item[data-menu] div.toggle_branch': '_onToggleSucursalClick',
    },
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.isMobile = config.device.isMobile;
        this._onSwitchSucursalClick = _.debounce(this._onSwitchSucursalClick, 1500, true);
    },

    /**
     * @override
     */
    willStart: function () {
        var self = this;
        this.allowed_branch_ids = String(session.user_context.allowed_branch_ids)
                                    .split(',')
                                    .map(function (id) {return parseInt(id);});
        this.user_branches = session.user_branches.allowed_branches;
        this.current_branch = this.allowed_branch_ids[0];
        this.current_branch_name = _.find(session.user_branches.allowed_branches, function (branch) {
            return branch[0] === self.current_branch;
        })[1];
        this.current_cmp_name = _.find(session.user_branches.allowed_branches, function (branch) {
            return branch[0] === self.current_branch;
        })[3];
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onSwitchSucursalClick: function (ev) {
        ev.stopPropagation();
        var dropdownItem = $(ev.currentTarget).parent();
        var dropdownMenu = dropdownItem.parent();
        var branchID = dropdownItem.data('branch-id');
        var allowed_branch_ids = this.allowed_branch_ids;
        var allowed_company_ids = String(session.user_context.allowed_company_ids) .split(',') .map(function (id) {return parseInt(id);});
        var cmpID = dropdownItem.data('cmp-id');
        if (dropdownItem.find('.fa-square-o').length) {
            // 1 enabled branch: Stay in single branch mode
            if (this.allowed_branch_ids.length === 1) {
                dropdownMenu.find('.fa-check-square').removeClass('fa-check-square').addClass('fa-square-o');
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                allowed_branch_ids = [branchID]
            } else { // Multi branch mode
                allowed_branch_ids.push(branchID);
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
            }
        }
        let pertenece = false;
        for(let indice = 0; indice < allowed_company_ids.length; indice ++) {
            let id_empresa = allowed_company_ids[indice]
            if(id_empresa == cmpID) {
                pertenece = true
            }
        }
        if(pertenece == false) { 
            allowed_branch_ids = [branchID];
        }
        session.setSucursales(branchID, allowed_branch_ids);
        if(pertenece == false) {            
            this.switch_branch_company(cmpID);
        }
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onToggleSucursalClick: function (ev) {
        ev.stopPropagation();
        var dropdownItem = $(ev.currentTarget).parent();
        var branchID = dropdownItem.data('branch-id');
        var allowed_branch_ids = this.allowed_branch_ids;
        var allowed_company_ids = String(session.user_context.allowed_company_ids).split(',') .map(function (id) {return parseInt(id);});
        var current_branch_id = allowed_branch_ids[0];
        var cmpID = dropdownItem.data('cmp-id');
        if (dropdownItem.find('.fa-square-o').length) {
            allowed_branch_ids.push(branchID);
            dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
        } else {
            allowed_branch_ids.splice(allowed_branch_ids.indexOf(branchID), 1);
            dropdownItem.find('.fa-check-square').addClass('fa-square-o').removeClass('fa-check-square');
        }
        
        let pertenece = false;
        for(let indice = 0; indice < allowed_company_ids.length; indice ++) {
            let id_empresa = allowed_company_ids[indice]
            if(id_empresa == cmpID) {
                pertenece = true
            }
        }
        if(pertenece == false) { 
            allowed_branch_ids = [branchID];
            current_branch_id = branchID;
        }
        session.setSucursales(current_branch_id, allowed_branch_ids);
        if(pertenece == false) {            
            this.switch_branch_company(cmpID);
        }
    },

    switch_branch_company: function(cmpID) {
		var self = this;
		session.user_companies.current_company[0] = cmpID;
        // set company name
        var company_name = '';
        for (var i=0; i<session.user_companies.allowed_companies.length; i++) {
			if (session.user_companies.allowed_companies[i][0] == cmpID) {
				company_name = session.user_companies.allowed_companies[i][1];
                break;
			}
		}
		session.user_companies.current_company[1] = company_name;
		$('.o_switch_company_menu .oe_topbar_name').text(session.user_companies.current_company[1]);
        session.user_context.allowed_company_ids = [cmpID];
        this.allowed_company_ids = String(session.user_context.allowed_company_ids)
                                    .split(',')
                                    .map(function (id) {return parseInt(id);});
        this.user_companies = session.user_companies.allowed_companies;
        this.current_company = cmpID;
        this.current_company_name = _.find(session.user_companies.allowed_companies, function (company) {
            return company[0] === self.current_company;
        })[1];
        session.setCompanies(cmpID, this.allowed_company_ids);
	}
});

if (session.display_switch_branch_menu) {
    SystrayMenu.Items.push(SwitchSucursalMenu);
}

return SwitchSucursalMenu;

});
