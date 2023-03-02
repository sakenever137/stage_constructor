odoo.define('stage_constructor.FormController', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var _t = core._t;
    var NCALayer = require('electronic_document_signature.open_form_dialog_without_mla');

    FormController.include({
        custom_events: _.extend({}, FormController.prototype.custom_events, {
            move_project: '_moveProject',
            create_record: '_createRecord',
            vote: '_vote',
        }),
    init: function () {
        initNcaLayer();
        this._super.apply(this, arguments);
    },
        _moveProject: function (event) {
            var self = this;
            console.log(event.target.res_id)
            return this.saveRecord.apply(this).then(function () {
                return self._rpc({
                    model: "stage.constructor",
                    domain: [["id", "=", event.data.route.id ]],
                    method: 'api_move_project',
                    args: [
                        [event.data.route.id],
                        event.target.res_id,
                    ],
                }).then(function () {
                    self.reload();
                });
            });
        },

        _createRecord: function (event){
            var ctx = {};
            ctx['default_project_id'] = this.initialState.data.id;
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: event.data.route.model,
                name : event.data.route.view_name,
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                res_id: false,
                context: {},
            });
        },

        _vote: function (event) {
            var self = this;
            return this.saveRecord.apply(this).then(function () {
                Dialog.confirm(self, _t("Are you sure that you want to approve the selected record?"), {
                    confirm_callback: function () {
                        return self._rpc({
                            model: "stage.constructor",
                            domain: [["id", "=", event.data.route.id ]],
                            method: 'api_vote_project',
                            args: [
                                 event.target.res_id,
                            ],
                        }).then(function () {
                            var to_approve = new NCALayer(self, self.initialState, {attrs: {string: 'Dialog'}});
                            var checker=to_approve.approve(self);
                      })
                    }});
            })
        },
    });

});
