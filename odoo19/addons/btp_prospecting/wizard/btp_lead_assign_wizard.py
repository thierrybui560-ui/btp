# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BtpLeadAssignWizard(models.TransientModel):
    """Wizard to assign leads to users"""
    _name = 'btp.lead.assign.wizard'
    _description = 'Assign BTP Leads'
    
    lead_ids = fields.Many2many(
        'btp.lead',
        string='Leads',
        required=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Assign To',
        required=True
    )
    is_open = fields.Boolean(
        string='Leave as Open',
        default=False,
        help='If checked, leads remain visible to all (common open)'
    )
    
    @api.model
    def default_get(self, fields_list):
        res = super(BtpLeadAssignWizard, self).default_get(fields_list)
        if self.env.context.get('active_ids'):
            res['lead_ids'] = [(6, 0, self.env.context['active_ids'])]
        return res
    
    def action_assign(self):
        """Assign leads to user"""
        self.ensure_one()
        
        self.lead_ids.write({
            'user_id': self.user_id.id,
            'is_open': self.is_open,
            'last_assigned_user_id': self.user_id.id,
            'claimed_date': fields.Datetime.now() if not self.is_open else False,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Leads Assigned'),
                'message': _('%s lead(s) assigned to %s.') % (len(self.lead_ids), self.user_id.name),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

