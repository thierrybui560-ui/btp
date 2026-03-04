# -*- coding: utf-8 -*-

import json
import logging
import time
from datetime import timedelta
import requests

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class BtpAiProvider(models.Model):
    _name = 'btp.ai.provider'
    _description = 'BTP AI Provider'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True,
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    provider_type = fields.Selection(
        [('openai_compatible', 'OpenAI Compatible')],
        required=True,
        default='openai_compatible',
    )
    endpoint = fields.Char(
        default='https://api.openai.com/v1/chat/completions',
        help='Chat completion endpoint for an OpenAI-compatible provider.',
    )
    model_name = fields.Char(required=True, default='gpt-4o-mini')
    api_key_config_param = fields.Char(
        required=True,
        default='btp_prospecting.ai_api_key',
        help='ir.config_parameter key that stores the provider API key.',
    )
    temperature = fields.Float(default=0.2)
    timeout_seconds = fields.Integer(default=30)
    retry_count = fields.Integer(
        default=2,
        help='Additional attempts when provider returns temporary failures (e.g., 429).',
    )

    @api.constrains('endpoint')
    def _check_endpoint(self):
        for rec in self:
            if rec.endpoint and not rec.endpoint.startswith('http'):
                raise ValidationError(_('Endpoint must start with http/https.'))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            self.env['btp.audit.log'].sudo().log(
                'create',
                model_name=rec._name,
                res_id=rec.id,
                reason=_('AI provider created: %s') % rec.name,
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
                reason=_('AI provider updated: %s') % rec.name,
                company_id=rec.company_id.id if rec.company_id else self.env.company.id,
            )
        return result

    def unlink(self):
        logs = [(rec.id, rec.name, rec.company_id.id if rec.company_id else self.env.company.id) for rec in self]
        result = super().unlink()
        for rec_id, rec_name, company_id in logs:
            self.env['btp.audit.log'].sudo().log(
                'unlink',
                model_name=self._name,
                res_id=rec_id,
                reason=_('AI provider deleted: %s') % rec_name,
                company_id=company_id,
            )
        return result

    def _get_api_key(self):
        self.ensure_one()
        return self.env['ir.config_parameter'].sudo().get_param(self.api_key_config_param)

    def run_prompt(self, prompt, system_prompt=None, max_tokens=500):
        self.ensure_one()
        started = fields.Datetime.now()
        ICP = self.env['ir.config_parameter'].sudo()
        ai_enabled = ICP.get_param('btp_prospecting.btp_ai_enabled', 'True') == 'True'
        if not ai_enabled:
            self.env['btp.ai.log'].sudo().create({
                'provider_id': self.id,
                'company_id': self.company_id.id or self.env.company.id,
                'model_name': self.model_name,
                'prompt': prompt,
                'system_prompt': system_prompt or '',
                'status': 'failed',
                'started_at': started,
                'finished_at': fields.Datetime.now(),
                'error_message': _('AI calls are disabled by governance setting.'),
            })
            return False

        daily_limit = int(ICP.get_param('btp_prospecting.btp_ai_daily_request_limit', '200') or 200)
        if daily_limit > 0:
            today = fields.Date.today()
            today_start = fields.Datetime.to_string(today)
            today_end = fields.Datetime.to_string(today + timedelta(days=1))
            used = self.env['btp.ai.log'].sudo().search_count([
                ('company_id', '=', self.company_id.id or self.env.company.id),
                ('started_at', '>=', today_start),
                ('started_at', '<', today_end),
            ])
            if used >= daily_limit:
                self.env['btp.ai.log'].sudo().create({
                    'provider_id': self.id,
                    'company_id': self.company_id.id or self.env.company.id,
                    'model_name': self.model_name,
                    'prompt': prompt,
                    'system_prompt': system_prompt or '',
                    'status': 'failed',
                    'started_at': started,
                    'finished_at': fields.Datetime.now(),
                    'error_message': _('AI daily request limit reached (%s).') % daily_limit,
                })
                return False

        log = self.env['btp.ai.log'].sudo().create({
            'provider_id': self.id,
            'company_id': self.company_id.id or self.env.company.id,
            'model_name': self.model_name,
            'prompt': prompt,
            'system_prompt': system_prompt or '',
            'status': 'running',
            'started_at': started,
        })
        api_key = self._get_api_key()
        if not api_key:
            log.write({
                'status': 'failed',
                'error_message': _('Missing API key in parameter: %s') % self.api_key_config_param,
                'finished_at': fields.Datetime.now(),
            })
            return False
        payload = {
            'model': self.model_name,
            'temperature': self.temperature,
            'max_tokens': max_tokens,
            'messages': [],
        }
        if system_prompt:
            payload['messages'].append({'role': 'system', 'content': system_prompt})
        payload['messages'].append({'role': 'user', 'content': prompt})
        headers = {
            'Authorization': 'Bearer %s' % api_key,
            'Content-Type': 'application/json',
        }

        attempts = max(1, 1 + int(self.retry_count or 0))
        last_error = False
        for attempt in range(1, attempts + 1):
            response = None
            try:
                response = requests.post(
                    self.endpoint,
                    headers=headers,
                    json=payload,
                    timeout=max(self.timeout_seconds, 5),
                )
                response.raise_for_status()
                data = response.json()
                text = (
                    data.get('choices', [{}])[0]
                    .get('message', {})
                    .get('content', '')
                )
                log.write({
                    'status': 'done',
                    'response': text,
                    'response_payload': json.dumps(data),
                    'finished_at': fields.Datetime.now(),
                })
                return text
            except Exception as exc:
                status_code = response.status_code if response is not None else None
                response_text = (response.text or '')[:500] if response is not None else ''
                last_error = str(exc)
                if response_text:
                    last_error = '%s | body=%s' % (last_error, response_text)

                # Retry only on temporary/provider throttling classes.
                should_retry = status_code in (408, 429, 500, 502, 503, 504)
                if attempt < attempts and should_retry:
                    retry_after = 0.0
                    if response is not None and response.headers.get('Retry-After'):
                        try:
                            retry_after = float(response.headers.get('Retry-After'))
                        except Exception:
                            retry_after = 0.0
                    backoff = retry_after if retry_after > 0 else float(2 ** (attempt - 1))
                    time.sleep(min(backoff, 10.0))
                    continue
                _logger.exception('AI provider call failed')
                break

        log.write({
            'status': 'failed',
            'error_message': last_error,
            'finished_at': fields.Datetime.now(),
        })
        return False
