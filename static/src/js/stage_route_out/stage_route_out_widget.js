odoo.define('stage_constructor.StageConstructorButtonWidget', function (require) {
    "use strict";

    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var StageConstructorButtonWidget = AbstractField.extend({

        _renderWidget: function () {
            var self = this;
            var value_json = JSON.parse(String(this.value).replace(/'/g, '"'));
            console.log(typeof value_json)
            if (!value_json.routes || !this.res_id) {
                return;
            }

            this.$el.addClass('o_statusbar_buttons');
            this.$el.addClass('stage_route_out_widget');
            this.$el.addClass('pr-1');

            _.each(value_json.routes, function (route) {
                var btn_style = route.btn_style === 'default'
                    ? 'btn-primary'
                    : 'btn-' + route.btn_style;

                var $route_btn = $('<button>')
                    .text(route.name)
                    .addClass('btn')
                    .addClass(btn_style)
                    .appendTo(self.$el);

                $route_btn.on('click', self._onBtnClick.bind(self, route));
            });
        },

        _renderEdit: function () {
            this._renderWidget();
        },

        _renderReadonly: function () {
            this._renderWidget();
        },

        _onBtnClick: function (route) {

        console.log(route.btn_type)
            if (route.btn_type === "move"){
                this.trigger_up('move_project', {
                    route: route,
                });
            }
            if (route.btn_type === "create") {
                this.trigger_up('create_record', {
                    route: route,
                });
            }
            if (route.btn_type === "voting") {
                this.trigger_up('vote', {
                    route_accept: route,
                });
            }
//            if (route.parent_id !== "undefined") {
//                this.trigger_up('vote', {
//                    route_reject: route,
//                });
//            }
        },
    });

    fieldRegistry.add('stage_btn_widget', StageConstructorButtonWidget);

    return StageConstructorButtonWidget;
});
