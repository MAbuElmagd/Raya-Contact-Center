odoo.define('wc_shaghalny.ShaghalnyReportListView', function (require) {
"use strict";

var ListView = require('web.ListView');
var ShaghalnyReportListController = require('wc_shaghalny.ShaghalnyReportListController');
var viewRegistry = require('web.view_registry');


var ShaghalnyReportListView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
        Controller: ShaghalnyReportListController,
    }),
});

viewRegistry.add('shaghalny_report_list', ShaghalnyReportListView);

return ShaghalnyReportListView;

});
