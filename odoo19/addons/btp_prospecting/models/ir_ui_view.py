# -*- coding: utf-8 -*-

from odoo import api, models


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def default_view(self, model, view_type):
        """In Odoo 19 list views use type 'list', not 'tree'. Map 'tree' to 'list' so
        actions/view_mode still using 'tree' resolve to the list view."""
        if view_type == 'tree':
            view_type = 'list'
        return super().default_view(model, view_type)
