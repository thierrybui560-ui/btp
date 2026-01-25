# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BtpLeadMergeWizard(models.TransientModel):
    """Wizard to merge duplicate leads"""
    _name = 'btp.lead.merge.wizard'
    _description = 'Merge BTP Leads'
    
    lead_ids = fields.Many2many(
        'btp.lead',
        string='Leads to Merge',
        required=True
    )
    target_lead_id = fields.Many2one(
        'btp.lead',
        string='Target Lead',
        required=True,
        help='Lead to keep (others will be merged into this one)'
    )
    merge_options = fields.Selection([
        ('keep_target', 'Keep Target Lead Data'),
        ('keep_newest', 'Keep Newest Data'),
        ('merge_all', 'Merge All Fields'),
    ], string='Merge Strategy', default='keep_target', required=True)
    
    @api.model
    def default_get(self, fields_list):
        res = super(BtpLeadMergeWizard, self).default_get(fields_list)
        if self.env.context.get('active_ids'):
            lead_ids = self.env.context['active_ids']
            res['lead_ids'] = [(6, 0, lead_ids)]
            if len(lead_ids) > 0:
                res['target_lead_id'] = lead_ids[0]  # First as default
        return res
    
    def action_merge(self):
        """Merge leads into target lead"""
        self.ensure_one()
        
        if len(self.lead_ids) < 2:
            raise UserError(_('Please select at least 2 leads to merge.'))
        
        if self.target_lead_id not in self.lead_ids:
            raise UserError(_('Target lead must be one of the selected leads.'))
        
        # Get leads to merge (excluding target)
        leads_to_merge = self.lead_ids - self.target_lead_id
        
        # Merge data based on strategy
        target = self.target_lead_id
        for lead in leads_to_merge:
            if self.merge_options == 'keep_target':
                # Keep target data, just merge history
                pass
            elif self.merge_options == 'keep_newest':
                # Keep newest non-empty values
                for field in target._fields:
                    if field in ['id', 'create_date', 'write_date', '__last_update']:
                        continue
                    if not target[field] and lead[field]:
                        target[field] = lead[field]
            elif self.merge_options == 'merge_all':
                # Merge all non-empty values from source
                for field in target._fields:
                    if field in ['id', 'create_date', 'write_date', '__last_update']:
                        continue
                    if not target[field] and lead[field]:
                        target[field] = lead[field]
            
            # Merge messages/history
            lead.message_ids.write({'res_id': target.id, 'model': 'btp.lead'})
            
            # Merge activities
            activities = self.env['mail.activity'].search([
                ('res_id', '=', lead.id),
                ('res_model', '=', 'btp.lead')
            ])
            activities.write({'res_id': target.id})
            
            # Mark as duplicate and link to original
            lead.write({
                'is_duplicate': True,
                'original_lead_id': target.id,
                'active': False,
            })
        
        # Update target lead
        target.write({
            'duplicate_ids': [(5, 0, 0)],  # Clear duplicates
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Merged Lead'),
            'res_model': 'btp.lead',
            'res_id': target.id,
            'view_mode': 'form',
            'target': 'current',
        }

