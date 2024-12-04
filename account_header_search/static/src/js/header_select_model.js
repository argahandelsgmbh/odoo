/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import {DateSearch} from "./date_search";
import {patch} from "@web/core/utils/patch";
import {
    AccountMoveListController
} from "@account/components/bills_upload/bills_upload";
import {useState} from "@odoo/owl";

patch(ListController.prototype,{
    setup(){
        super.setup()
        this.state = useState({
            date_search: false,
        });
    }
})

patch(AccountMoveListController.prototype,{
    setup(){
        super.setup()
        this.state = useState({
            date_search: true,
        });
    }
})

patch(AccountMoveListController.components,Object.assign({}, ListController.components, {DateSearch}))