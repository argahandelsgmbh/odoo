/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import {DateSearch} from "./date_search";
import {patch} from "@web/core/utils/patch";
import { SaleOrderListController } from "./sale_order_list";
import {useState} from "@odoo/owl";

patch(ListController.prototype,{
    setup(){
        super.setup()
        this.state = useState({
            sale_date_search: false,
        });
    }
})

patch(SaleOrderListController.prototype,{
    setup(){
        super.setup()
        this.state = useState({
            sale_date_search: true,
        });
    }
})

patch(SaleOrderListController.components,Object.assign({}, ListController.components, {DateSearch}))