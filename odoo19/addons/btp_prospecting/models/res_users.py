# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    """Extend users to support pyramidal hierarchy for lead visibility"""
    _inherit = 'res.users'
    
    # Round-robin availability and weight (BTP lead assignment)
    btp_is_unavailable = fields.Boolean(
        string='BTP Unavailable',
        default=False,
        help='If enabled, the user is skipped by BTP round-robin assignment.'
    )
    btp_is_overloaded = fields.Boolean(
        string='BTP Overloaded',
        default=False,
        help='If enabled, the user is skipped by BTP round-robin assignment.'
    )
    btp_round_robin_weight = fields.Integer(
        string='BTP Round-Robin Weight',
        default=1,
        help='Higher weight means the user receives more leads in round-robin.'
    )

    # Pyramidal hierarchy
    manager_id = fields.Many2one(
        'res.users',
        string='Manager',
        help='Direct manager for pyramidal hierarchy'
    )
    subordinate_ids = fields.One2many(
        'res.users',
        'manager_id',
        string='Subordinates',
        help='Direct subordinates'
    )
    all_subordinate_ids = fields.Many2many(
        'res.users',
        'user_subordinate_rel',
        'manager_id',
        'subordinate_id',
        string='All Subordinates',
        compute='_compute_all_subordinates',
        help='All subordinates (recursive)'
    )
    
    @api.depends('subordinate_ids')
    def _compute_all_subordinates(self):
        for user in self:
            subordinates = user.subordinate_ids
            # Recursively get all subordinates
            processed = set([user.id])
            to_process = list(user.subordinate_ids.ids)
            
            while to_process:
                current_id = to_process.pop(0)
                if current_id in processed:
                    continue
                processed.add(current_id)
                current_user = self.browse(current_id)
                if current_user.subordinate_ids:
                    new_subordinates = current_user.subordinate_ids - subordinates
                    subordinates |= new_subordinates
                    to_process.extend(new_subordinates.ids)
            
            user.all_subordinate_ids = subordinates
    
    def get_visible_lead_domain(self):
        """Get domain for leads visible to this user (pyramidal hierarchy)"""
        self.ensure_one()
        
        # User can see:
        # 1. Own leads
        # 2. Open leads (common open)
        # 3. Subordinates' leads (if manager)
        
        domain = ['|', ('is_open', '=', True), ('user_id', '=', self.id)]
        
        if self.all_subordinate_ids:
            domain = ['|'] + domain + [('user_id', 'in', self.all_subordinate_ids.ids)]
        
        return domain

