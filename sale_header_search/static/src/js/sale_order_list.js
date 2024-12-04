/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";

import { Component, useState } from "@odoo/owl";

export class SaleOrderListController extends ListController {
    setup() {
        super.setup();
    }
};

SaleOrderListController.components = {
    ...ListController.components,
};

export const SaleOrderListView = {
    ...listView,
    Controller: SaleOrderListController,
};

registry.category("views").add("sale_header_search", SaleOrderListView);
