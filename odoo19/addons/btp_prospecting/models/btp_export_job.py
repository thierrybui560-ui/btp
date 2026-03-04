# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 11 — Reports & Exports

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BtpExportJob(models.Model):
    _name = 'btp.export.job'
    _description = 'BTP Report Export Job'
    _order = 'run_date desc, id desc'

    report_template_id = fields.Many2one(
        'btp.report.template',
        string='Report Template',
        required=True,
        ondelete='cascade',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='report_template_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )
    run_date = fields.Datetime(string='Run Date', default=fields.Datetime.now, readonly=True)
    state = fields.Selection(
        [('pending', 'Pending'), ('done', 'Done'), ('failed', 'Failed')],
        string='Status',
        default='pending',
        required=True,
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Generated File',
        ondelete='set null',
        readonly=True,
    )
    error_message = fields.Text(string='Error', readonly=True)

    def action_download(self):
        """Download the generated file."""
        self.ensure_one()
        if self.state != 'done' or not self.attachment_id:
            raise UserError(_('No file available for download.'))
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=1' % self.attachment_id.id,
            'target': 'self',
        }

    def _send_report_email(self, attachment):
        """Send report by email to recipient_user_ids of the template."""
        self.ensure_one()
        template = self.report_template_id
        if not template.recipient_user_ids:
            return
        subject = _('BTP Report: %s') % template.name
        body = _(
            'Please find attached the report "%s" (generated on %s).'
        ) % (template.name, self.run_date.strftime('%Y-%m-%d %H:%M'))
        for user in template.recipient_user_ids:
            if template.company_id and template.company_id not in user.company_ids:
                continue
            if not user.email:
                continue
            mail_values = {
                'subject': subject,
                'body_html': '<p>%s</p>' % body,
                'email_to': user.email,
                'attachment_ids': [(4, attachment.id)],
            }
            self.env['mail.mail'].sudo().create(mail_values).send()
