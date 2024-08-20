/** @odoo-module **/
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";

export class NavIcon extends Component {
    static template = "roryx_online_order_V17.NavIcon";
    setup() {
        this.orm = useService("orm");
        this.pos = usePos();
        this.popup = useService("popup");
    }
    async onClick() {
       var self = this
       await this.orm.call(
            "pos.order", "find_online_wera_order", [], {}
        ).then(function(result) {
            self.pos.showScreen('CustomScreen', {
                data: result,
            });
        })
    }
}
Navbar.components = { ...Navbar.components,NavIcon };
