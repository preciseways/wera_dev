/** @odoo-module **/
/*
 * This file is used to register a new screen for Booked orders.
 */
import { registry } from "@web/core/registry";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";

class CustomScreen extends TicketScreen {
    static template = "roryx_online_order_V17.CustomScreen";
    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
    }
    back() {
        this.pos.ticket_screen_mobile_pane = "left";
        this.pos.closeScreen();   
    }
}
registry.category("pos_screens").add("CustomScreen", CustomScreen);
