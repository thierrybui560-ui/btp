# -*- coding: utf-8 -*-

import json
import logging
import requests
from datetime import datetime
from xml.etree import ElementTree

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class BtpTenderWatchRun(models.Model):
    _name = 'btp.tender.watch.run'
    _description = 'BTP Tender Watch Run'
    _order = 'id desc'

    source_id = fields.Many2one('btp.tender.source', required=True, ondelete='cascade')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='source_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )
    started_at = fields.Datetime(default=fields.Datetime.now, required=True)
    finished_at = fields.Datetime()
    status = fields.Selection(
        [('running', 'Running'), ('done', 'Done'), ('failed', 'Failed')],
        default='running',
    )
    lead_created_count = fields.Integer(default=0)
    error_message = fields.Text()
    payload_excerpt = fields.Text()

    @api.model
    def _cron_fetch_tenders(self):
        runs = self.env['btp.tender.watch.run']
        created_total = 0
        for source in self.env['btp.tender.source'].search([('active', '=', True)]):
            run = runs.create({'source_id': source.id})
            try:
                created = self._fetch_source(source, run)
                created_total += created
                run.write({
                    'status': 'done',
                    'finished_at': fields.Datetime.now(),
                    'lead_created_count': created,
                })
                source.last_fetch_at = fields.Datetime.now()
            except Exception as exc:
                _logger.exception('Tender watch failed for source %s', source.id)
                run.write({
                    'status': 'failed',
                    'finished_at': fields.Datetime.now(),
                    'error_message': str(exc),
                })
        return created_total

    @api.model
    def _fetch_source(self, source, run):
        response = requests.get(source.url, timeout=30)
        response.raise_for_status()
        content = response.text or ''
        run.payload_excerpt = content[:4000]
        if source.source_type == 'rss':
            return self._ingest_rss(source, content)
        return self._ingest_json(source, content)

    @api.model
    def _ingest_json(self, source, content):
        payload = json.loads(content or '{}')
        if isinstance(payload, dict):
            rows = payload.get('items', [])
        else:
            rows = payload
        return self._create_leads_from_rows(source, rows)

    @api.model
    def _ingest_rss(self, source, content):
        root = ElementTree.fromstring(content.encode('utf-8'))
        items = []
        for item in root.findall('.//item'):
            title = (item.findtext('title') or '').strip()
            desc = (item.findtext('description') or '').strip()
            pub_date = (item.findtext('pubDate') or '').strip()
            link = (item.findtext('link') or '').strip()
            items.append({
                'title': title,
                'summary': desc,
                'published_at': pub_date,
                'url': link,
            })
        return self._create_leads_from_rows(source, items)

    @api.model
    def _create_leads_from_rows(self, source, rows):
        Lead = self.env['btp.lead']
        created = 0
        for row in rows[:100]:
            title = (row.get('title') or row.get('name') or '').strip()
            if not title:
                continue
            exists = Lead.search([('name', '=', title), ('origin', '=', 'tender')], limit=1)
            if exists:
                continue
            deadline = row.get('deadline')
            deadline_date = False
            if isinstance(deadline, str):
                try:
                    deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00')).date()
                except Exception:
                    deadline_date = False
            Lead.create({
                'name': title[:255],
                'origin': 'tender',
                'origin_detail': source.name,
                'description': row.get('summary') or row.get('description') or row.get('url') or '',
                'tender_deadline': deadline_date,
                'company_id': source.default_company_id.id or self.env.company.id,
                'is_open': bool(source.default_open_mode),
                'user_id': False if source.default_open_mode else self.env.user.id,
            })
            created += 1
        return created
