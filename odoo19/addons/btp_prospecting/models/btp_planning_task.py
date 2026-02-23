# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    """Extend project.task for BTP planning: link to quote item, Gantt, yield/pointing/consumption."""
    _inherit = 'project.task'

    btp_quote_item_id = fields.Many2one(
        'btp.quote.item',
        string='Quote Item',
        ondelete='set null',
        index=True,
        help='Quote item (Lot → Title → Subtitle → Item) this task comes from when planning is generated from quote.'
    )
    btp_planned_qty = fields.Float(
        string='Planned Quantity',
        digits='Product Unit of Measure',
        help='Planned quantity from quote item (m², ml, etc.)'
    )
    btp_uom_id = fields.Many2one(
        'uom.uom',
        string='UoM',
        help='Unit of measure for planned/actual quantity'
    )
    btp_yield_entry_ids = fields.One2many(
        'btp.site.performance',
        'task_id',
        string='Yield Entries',
        help='Daily yield entries (planned vs actual) for this task'
    )
    btp_pointing_ids = fields.One2many(
        'btp.site.pointing',
        'task_id',
        string='Pointing Entries',
        help='Team/person pointing on this task'
    )
    btp_consumption_ids = fields.One2many(
        'btp.site.consumption',
        'task_id',
        string='Consumptions',
        help='Article consumptions linked to this task'
    )

    def _btp_from_quote_item_vals(self, item, project, sequence, date_start, date_end):
        """Build task vals from a quote item for planning generation."""
        return {
            'name': item.name,
            'project_id': project.id,
            'btp_quote_item_id': item.id,
            'btp_planned_qty': item.quantity,
            'btp_uom_id': item.uom_id.id if item.uom_id else False,
            'sequence': sequence,
            'date_deadline': date_end,
            'date_assign': date_start,
            'user_ids': [(6, 0, project.user_id.ids)] if project.user_id else [],
        }
