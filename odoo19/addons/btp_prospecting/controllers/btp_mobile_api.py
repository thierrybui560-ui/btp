# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 14 — Mobile Application (Android & iOS): JSON API for PWA and native clients.

import logging
from datetime import date
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


def _mobile_json_response(success, data=None, error=None):
    """Standard JSON response for mobile API."""
    out = {'success': success}
    if data is not None:
        out['data'] = data
    if error is not None:
        out['error'] = error
    return out


class BtpMobileApiController(http.Controller):
    """Module 14 — Mobile API: leads, sites, quotes, pointing, yields, QHSE, tasks, dashboard, notifications."""

    # ---------- Leads ----------
    @http.route('/btp/mobile/leads', type='json', auth='user')
    def leads_list(self, limit=50, offset=0):
        """List leads assigned to current user (or common open)."""
        try:
            domain = [
                ('active', '=', True),
                '|',
                ('user_id', '=', request.env.user.id),
                '&', ('is_open', '=', True), ('converted', '=', False),
            ]
            leads = request.env['btp.lead'].search(domain, limit=limit, offset=offset, order='create_date desc')
            return _mobile_json_response(True, [{
                'id': l.id,
                'name': l.name,
                'partner_name': l.partner_name or (l.partner_id.name if l.partner_id else None),
                'site_name': l.site_name,
                'stage_id': l.stage_id.id if l.stage_id else None,
                'stage_name': l.stage_id.name if l.stage_id else None,
                'user_id': l.user_id.id if l.user_id else None,
                'create_date': l.create_date.isoformat() if l.create_date else None,
                'converted': l.converted,
            } for l in leads])
        except Exception as e:
            _logger.exception('btp/mobile/leads list')
            return _mobile_json_response(False, error=str(e))

    @http.route('/btp/mobile/lead/create', type='json', auth='user')
    def lead_create(self, **kwargs):
        """Create lead from field (optionally with photo base64)."""
        try:
            lead_vals = {
                'name': kwargs.get('name') or _('Mobile Lead'),
                'origin': 'field',
                'origin_detail': kwargs.get('origin_detail') or 'Mobile App',
                'site_name': kwargs.get('site_name'),
                'site_address': kwargs.get('site_address'),
                'site_city': kwargs.get('site_city'),
                'site_zip': kwargs.get('site_zip'),
                'site_type': kwargs.get('site_type'),
                'partner_name': kwargs.get('partner_name'),
                'partner_email': kwargs.get('partner_email'),
                'partner_phone': kwargs.get('partner_phone'),
                'description': kwargs.get('description'),
            }
            country_id = kwargs.get('site_country_id')
            if country_id:
                try:
                    lead_vals['site_country_id'] = int(country_id)
                except (TypeError, ValueError):
                    pass
            lead = request.env['btp.lead'].create(lead_vals)
            # Auto-assign to creator (assignment rules may override)
            if not lead.user_id:
                lead.user_id = request.env.user.id
            # Optional: attach photo
            photo_b64 = kwargs.get('photo_base64')
            if photo_b64:
                try:
                    request.env['ir.attachment'].create({
                        'name': 'lead_photo_%s.jpg' % lead.id,
                        'datas': photo_b64,
                        'res_model': 'btp.lead',
                        'res_id': lead.id,
                    })
                except Exception as att_e:
                    _logger.warning('Lead photo attach failed: %s', att_e)
            return _mobile_json_response(True, {'lead_id': lead.id, 'message': _('Lead created successfully')})
        except Exception as e:
            _logger.exception('btp/mobile/lead/create')
            return _mobile_json_response(False, error=str(e))

    # ---------- Partners (clients/contacts) ----------
    @http.route('/btp/mobile/partners', type='json', auth='user')
    def partners_list(self, limit=100, offset=0, search=None):
        """List clients/contacts accessible to current user (record rules apply)."""
        try:
            domain = []
            if search:
                domain = ['|', ('name', 'ilike', search), ('email', 'ilike', search)]
            partners = request.env['res.partner'].search(
                domain, limit=limit, offset=offset, order='name'
            )
            return _mobile_json_response(True, [{
                'id': p.id,
                'name': p.name,
                'is_company': p.is_company,
                'email': p.email,
                'phone': p.phone or p.mobile,
                'city': p.city,
            } for p in partners])
        except Exception as e:
            _logger.exception('btp/mobile/partners')
            return _mobile_json_response(False, error=str(e))

    # ---------- Quotes ----------
    @http.route('/btp/mobile/quotes', type='json', auth='user')
    def quotes_list(self, limit=50, offset=0, state=None):
        """List sale orders (quotes) for current user."""
        try:
            domain = [('btp_quote_number', '!=', False)]
            if state:
                domain.append(('state', '=', state))
            orders = request.env['sale.order'].search(
                domain, limit=limit, offset=offset, order='date_order desc'
            )
            return _mobile_json_response(True, [{
                'id': o.id,
                'name': o.name,
                'btp_quote_number': o.btp_quote_number,
                'partner_id': o.partner_id.id,
                'partner_name': o.partner_id.name if o.partner_id else None,
                'state': o.state,
                'amount_total': o.amount_total,
                'date_order': o.date_order.isoformat() if o.date_order else None,
            } for o in orders])
        except Exception as e:
            _logger.exception('btp/mobile/quotes')
            return _mobile_json_response(False, error=str(e))

    @http.route('/btp/mobile/quote/<int:order_id>', type='json', auth='user')
    def quote_get(self, order_id):
        """Get one quote and PDF report URL if available."""
        try:
            order = request.env['sale.order'].browse(order_id)
            if not order.exists():
                return _mobile_json_response(False, error=_('Quote not found'))
            report = request.env.ref('sale.action_report_saleorder', raise_if_not_found=False)
            pdf_url = None
            if report and report.report_type in ('qweb-pdf', 'qweb-html'):
                pdf_url = '/report/pdf/sale.report_saleorder/%s' % order_id
            return _mobile_json_response(True, {
                'id': order.id,
                'name': order.name,
                'btp_quote_number': order.btp_quote_number,
                'partner_name': order.partner_id.name if order.partner_id else None,
                'state': order.state,
                'amount_total': order.amount_total,
                'pdf_url': pdf_url,
            })
        except Exception as e:
            _logger.exception('btp/mobile/quote get')
            return _mobile_json_response(False, error=str(e))

    # ---------- Sites ----------
    @http.route('/btp/mobile/sites', type='json', auth='user')
    def sites_list(self, limit=50, offset=0, active_only=True):
        """List BTP sites (project.project with btp_site_code)."""
        try:
            domain = [('btp_site_code', '!=', False)]
            if active_only:
                domain.append(('active', '=', True))
            sites = request.env['project.project'].search(
                domain, limit=limit, offset=offset, order='btp_site_code desc'
            )
            return _mobile_json_response(True, [{
                'id': s.id,
                'name': s.name,
                'btp_site_code': s.btp_site_code,
                'partner_id': s.partner_id.id if s.partner_id else None,
                'partner_name': s.partner_id.name if s.partner_id else None,
                'btp_start_date': s.btp_start_date.isoformat() if s.btp_start_date else None,
                'btp_end_date_planned': s.btp_end_date_planned.isoformat() if s.btp_end_date_planned else None,
            } for s in sites])
        except Exception as e:
            _logger.exception('btp/mobile/sites')
            return _mobile_json_response(False, error=str(e))

    @http.route('/btp/mobile/site/<int:site_id>/documents', type='json', auth='user')
    def site_documents(self, site_id):
        """List documents attached to a site (btp.site.document and chatter)."""
        try:
            site = request.env['project.project'].browse(site_id)
            if not site.exists() or not site.btp_site_code:
                return _mobile_json_response(False, error=_('Site not found'))
            docs = request.env['btp.site.document'].search([('site_id', '=', site_id)])
            return _mobile_json_response(True, [{
                'id': d.id,
                'name': d.name or d.document_type or 'Document',
                'document_type': d.document_type,
                'attachment_id': d.attachment_id.id if d.attachment_id else None,
                'attachment_name': d.attachment_id.name if d.attachment_id else None,
            } for d in docs])
        except Exception as e:
            _logger.exception('btp/mobile/site/documents')
            return _mobile_json_response(False, error=str(e))

    # ---------- Pointing ----------
    @http.route('/btp/mobile/pointing/create', type='json', auth='user')
    def pointing_create(self, site_id, date=None, user_id=None, subcontractor_id=None, hours=0, qty_done=0, notes=None):
        """Submit a pointing entry for a site (by day, employee or subcontractor)."""
        try:
            site = request.env['project.project'].browse(int(site_id))
            if not site.exists():
                return _mobile_json_response(False, error=_('Site not found'))
            vals = {
                'site_id': site.id,
                'user_id': int(user_id) if user_id else None,
                'subcontractor_id': int(subcontractor_id) if subcontractor_id else None,
                'hours': float(hours or 0),
                'qty_done': float(qty_done or 0),
                'notes': notes,
            }
            if date:
                vals['date'] = date
            if not vals['user_id'] and not vals['subcontractor_id']:
                vals['user_id'] = request.env.user.id
            entry = request.env['btp.site.pointing'].create(vals)
            return _mobile_json_response(True, {'id': entry.id, 'message': _('Pointing saved')})
        except Exception as e:
            _logger.exception('btp/mobile/pointing/create')
            return _mobile_json_response(False, error=str(e))

    # ---------- Yield ----------
    @http.route('/btp/mobile/yield/create', type='json', auth='user')
    def yield_create(self, task_id, date=None, expected_qty=0, real_qty=0, notes=None):
        """Submit a yield entry (daily executed quantities) for a task."""
        try:
            task = request.env['project.task'].browse(int(task_id))
            if not task.exists():
                return _mobile_json_response(False, error=_('Task not found'))
            vals = {
                'task_id': task.id,
                'expected_qty': float(expected_qty or 0),
                'real_qty': float(real_qty or 0),
                'notes': notes,
            }
            if date:
                vals['date'] = date
            entry = request.env['btp.site.performance'].create(vals)
            return _mobile_json_response(True, {'id': entry.id, 'message': _('Yield saved')})
        except Exception as e:
            _logger.exception('btp/mobile/yield/create')
            return _mobile_json_response(False, error=str(e))

    # ---------- QHSE Incident ----------
    @http.route('/btp/mobile/incident/create', type='json', auth='user')
    def incident_create(self, site_id, description, incident_type='incident', location=None, photo_base64=None, **kwargs):
        """Declare a QHSE incident (with optional photo)."""
        try:
            site = request.env['project.project'].browse(int(site_id))
            if not site.exists() or not site.btp_site_code:
                return _mobile_json_response(False, error=_('Site not found'))
            vals = {
                'site_id': site.id,
                'description': description,
                'incident_type': incident_type,
                'severity': kwargs.get('severity') or 'medium',
                'location': location,
                'concerned_team': kwargs.get('concerned_team'),
                'user_id': request.env.user.id,
            }
            incident = request.env['btp.qse.incident'].create(vals)
            if photo_base64:
                try:
                    request.env['ir.attachment'].create({
                        'name': 'incident_%s.jpg' % incident.id,
                        'datas': photo_base64,
                        'res_model': 'btp.qse.incident',
                        'res_id': incident.id,
                    })
                except Exception as att_e:
                    _logger.warning('Incident photo attach failed: %s', att_e)
            return _mobile_json_response(True, {'id': incident.id, 'name': incident.name, 'message': _('Incident declared')})
        except Exception as e:
            _logger.exception('btp/mobile/incident/create')
            return _mobile_json_response(False, error=str(e))

    # ---------- Tasks / Activities ----------
    @http.route('/btp/mobile/tasks', type='json', auth='user')
    def tasks_list(self, limit=30):
        """List current user's mail activities (reminders, to-dos)."""
        try:
            activities = request.env['mail.activity'].search([
                ('user_id', '=', request.env.user.id),
            ], limit=limit, order='date_deadline asc')
            return _mobile_json_response(True, [{
                'id': a.id,
                'activity_type_id': a.activity_type_id.id,
                'summary': a.summary or a.activity_type_id.display_name if a.activity_type_id else None,
                'date_deadline': a.date_deadline.isoformat() if a.date_deadline else None,
                'res_model': a.res_model,
                'res_id': a.res_id,
            } for a in activities])
        except Exception as e:
            _logger.exception('btp/mobile/tasks')
            return _mobile_json_response(False, error=str(e))

    # ---------- Dashboard / KPIs ----------
    @http.route('/btp/mobile/dashboard', type='json', auth='user')
    def dashboard(self):
        """Mobile dashboard KPIs by role (salesperson, site manager, management)."""
        try:
            user = request.env.user
            is_manager = user.has_group('btp_prospecting.group_btp_manager') or user.has_group('btp_prospecting.group_btp_admin')
            data = {}
            # Leads
            lead_domain = [('active', '=', True), ('converted', '=', False)]
            if not is_manager:
                lead_domain.append('|')
                lead_domain.append(('user_id', '=', user.id))
                lead_domain.append(('is_open', '=', True))
            leads = request.env['btp.lead'].search(lead_domain)
            data['leads_count'] = len(leads)
            today = date.today()
            first_of_month = today.replace(day=1)
            data['leads_converted_this_month'] = request.env['btp.lead'].search_count([
                ('converted', '=', True),
                ('converted_date', '>=', first_of_month),
            ])
            # Quotes
            quote_domain = [('btp_quote_number', '!=', False), ('state', 'in', ('draft', 'sent'))]
            data['quotes_pending'] = request.env['sale.order'].search_count(quote_domain)
            # Sites
            data['sites_active'] = request.env['project.project'].search_count([
                ('btp_site_code', '!=', False), ('active', '=', True)
            ])
            # Activities (current user)
            data['activities_count'] = request.env['mail.activity'].search_count([
                ('user_id', '=', user.id),
            ])
            return _mobile_json_response(True, data)
        except Exception as e:
            _logger.exception('btp/mobile/dashboard')
            return _mobile_json_response(False, error=str(e))

    # ---------- Notifications / Alerts (for push or pull) ----------
    @http.route('/btp/mobile/notifications', type='json', auth='user')
    def notifications(self, limit=20):
        """List alerts: quote reminders, expired docs, site delays, new tasks. For PWA or native app to poll or display."""
        try:
            alerts = []
            user = request.env.user
            today = date.today()
            # Overdue activities
            overdue = request.env['mail.activity'].search([
                ('user_id', '=', user.id),
                ('date_deadline', '<', str(today)),
            ], limit=5)
            for a in overdue:
                alerts.append({
                    'type': 'task_overdue',
                    'title': _('Overdue task'),
                    'body': a.summary or (a.res_model and a.res_id and '%s #%s' % (a.res_model, a.res_id)) or '',
                    'res_model': a.res_model,
                    'res_id': a.res_id,
                })
            # Quote follow-up (simplified: quotes in draft/sent with next_followup in past)
            quotes = request.env['sale.order'].search([
                ('btp_quote_number', '!=', False),
                ('state', 'in', ('draft', 'sent')),
                ('btp_next_followup_date', '!=', False),
                ('btp_next_followup_date', '<=', str(today)),
            ], limit=5)
            for q in quotes:
                alerts.append({
                    'type': 'quote_reminder',
                    'title': _('Quote reminder'),
                    'body': q.name + (' - ' + (q.partner_id.name or '')) if q.partner_id else q.name,
                    'res_model': 'sale.order',
                    'res_id': q.id,
                })
            return _mobile_json_response(True, alerts[:limit])
        except Exception as e:
            _logger.exception('btp/mobile/notifications')
            return _mobile_json_response(False, error=str(e))
