# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class BtpLeadController(http.Controller):
    """Web controller for BTP Lead creation forms"""

    @http.route('/btp/lead/create', type='http', auth='public', methods=['GET', 'POST'], website=True, csrf=False)
    def create_lead_form(self, **kwargs):
        """Public web form to create a lead"""
        if request.httprequest.method == 'POST':
            try:
                # Create lead from form data
                lead_vals = {
                    'name': kwargs.get('name', 'Web Lead'),
                    'origin': 'web',
                    'origin_detail': kwargs.get('origin_detail', 'Web Form'),
                    'site_name': kwargs.get('site_name'),
                    'site_address': kwargs.get('site_address'),
                    'site_city': kwargs.get('site_city'),
                    'site_zip': kwargs.get('site_zip'),
                    'site_country_id': int(kwargs.get('site_country_id', 0)) if kwargs.get('site_country_id') else False,
                    'site_type': kwargs.get('site_type'),
                    'partner_name': kwargs.get('partner_name'),
                    'partner_email': kwargs.get('partner_email'),
                    'partner_phone': kwargs.get('partner_phone'),
                    'description': kwargs.get('description'),
                    'is_open': True,  # Web leads start as open
                }
                
                lead = request.env['btp.lead'].sudo().create(lead_vals)
                
                return request.render('btp_prospecting.lead_form_success', {
                    'lead': lead,
                })
            except Exception as e:
                _logger.error(f"Error creating lead from web form: {e}")
                return request.render('btp_prospecting.lead_form_error', {
                    'error': str(e),
                })
        
        # GET request - show form
        countries = request.env['res.country'].sudo().search([])
        return request.render('btp_prospecting.lead_form_template', {
            'countries': countries,
        })

    @http.route('/btp/lead/mobile', type='json', auth='user', methods=['POST'])
    def create_lead_mobile(self, **kwargs):
        """JSON endpoint for mobile app to create leads"""
        try:
            lead_vals = {
                'name': kwargs.get('name', 'Mobile Lead'),
                'origin': 'field',
                'origin_detail': kwargs.get('origin_detail', 'Mobile App'),
                'site_name': kwargs.get('site_name'),
                'site_address': kwargs.get('site_address'),
                'site_city': kwargs.get('site_city'),
                'site_zip': kwargs.get('site_zip'),
                'site_country_id': kwargs.get('site_country_id'),
                'site_type': kwargs.get('site_type'),
                'partner_name': kwargs.get('partner_name'),
                'description': kwargs.get('description'),
                'user_id': request.env.user.id,  # Auto-assign to creator
            }
            
            lead = request.env['btp.lead'].create(lead_vals)
            
            return {
                'success': True,
                'lead_id': lead.id,
                'message': 'Lead created successfully',
            }
        except Exception as e:
            _logger.error(f"Error creating lead from mobile: {e}")
            return {
                'success': False,
                'error': str(e),
            }

