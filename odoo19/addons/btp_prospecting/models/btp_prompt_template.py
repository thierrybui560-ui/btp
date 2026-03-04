# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BtpPromptTemplate(models.Model):
    _name = 'btp.prompt.template'
    _description = 'BTP Prompt Template'
    _order = 'name, version desc'

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True,
    )
    code = fields.Char(required=True, help='Stable key used by automations, e.g. lead_briefing.')
    version = fields.Integer(default=1)
    active = fields.Boolean(default=True)
    system_prompt = fields.Text()
    user_prompt_template = fields.Text(required=True)
    provider_id = fields.Many2one('btp.ai.provider', required=True, ondelete='restrict')

    _sql_constraints = [
        ('btp_prompt_template_code_version_unique', 'unique(code, version)', 'Prompt code/version must be unique.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            self.env['btp.audit.log'].sudo().log(
                'create',
                model_name=rec._name,
                res_id=rec.id,
                reason=_('Prompt template created: %s v%s') % (rec.code, rec.version),
                company_id=rec.company_id.id if rec.company_id else self.env.company.id,
            )
        return records

    def write(self, vals):
        result = super().write(vals)
        for rec in self:
            self.env['btp.audit.log'].sudo().log(
                'write',
                model_name=rec._name,
                res_id=rec.id,
                reason=_('Prompt template updated: %s v%s') % (rec.code, rec.version),
                company_id=rec.company_id.id if rec.company_id else self.env.company.id,
            )
        return result

    def unlink(self):
        logs = [(rec.id, rec.code, rec.version, rec.company_id.id if rec.company_id else self.env.company.id) for rec in self]
        result = super().unlink()
        for rec_id, rec_code, rec_version, company_id in logs:
            self.env['btp.audit.log'].sudo().log(
                'unlink',
                model_name=self._name,
                res_id=rec_id,
                reason=_('Prompt template deleted: %s v%s') % (rec_code, rec_version),
                company_id=company_id,
            )
        return result

    def render(self, variables):
        self.ensure_one()
        text = self.user_prompt_template or ''
        for key, value in (variables or {}).items():
            text = text.replace('{{%s}}' % key, str(value if value is not None else ''))
        return text

    def run_with_variables(self, variables=None, max_tokens=500):
        self.ensure_one()
        if not self.provider_id:
            raise UserError(_('No AI provider configured on prompt template "%s".') % self.display_name)
        prompt = self.render(variables or {})
        return self.provider_id.run_prompt(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=max_tokens,
        )
