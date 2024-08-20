/** @odoo-module **/
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { url } from "@web/core/utils/urls";

export const iapNotificationService = {
    dependencies: ["bus_service", "notification","sound"],

    start(env, { bus_service, notification }) {
        bus_service.subscribe("POS_ORDER_CREATION_NOTIFICATION", (params) => {
            displayNotification(params);
        });
        bus_service.start();
        function displayNotification(params) {
            const message = `${params.data} Order Created`;
            notification.add(message, {
                title: "Order Created",
                type: 'info',
            });
            playSound();
        }

        async function playSound() {
            const audio = new Audio('/roryx_online_order_V17/static/src/sound/exclamation.wav');
            audio.play();
        }
    }
};

registry.category("services").add("iapNotification", iapNotificationService);
