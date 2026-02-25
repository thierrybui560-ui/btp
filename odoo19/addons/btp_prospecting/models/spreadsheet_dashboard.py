# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE file for full copyright and licensing details.

import base64
import json
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class SpreadsheetDashboard(models.Model):
    _inherit = "spreadsheet.dashboard"

    def _get_serialized_readonly_dashboard(self):
        """Use binary data when computed spreadsheet_data is missing; fall back to sample when filestore is missing."""
        try:
            snapshot = None
            if self.spreadsheet_data:
                snapshot = json.loads(self.spreadsheet_data)
            elif self.spreadsheet_binary_data:
                snapshot = json.loads(
                    base64.b64decode(self.spreadsheet_binary_data).decode()
                )
            if snapshot is None:
                return self._get_serialized_sample_fallback()
            user_locale = self.env['res.lang']._get_user_spreadsheet_locale()
            snapshot.setdefault('settings', {})['locale'] = user_locale
            default_currency = self.env['res.currency'].get_company_currency_for_spreadsheet()
            return json.dumps({
                'snapshot': snapshot,
                'revisions': [],
                'default_currency': default_currency,
                'translation_namespace': self._get_dashboard_translation_namespace(),
            })
        except (FileNotFoundError, OSError, TypeError, ValueError, json.JSONDecodeError) as e:
            _logger.warning(
                "Spreadsheet dashboard %s: could not load data (%s), trying sample fallback.",
                self.display_name,
                e,
                exc_info=True,
            )
            return self._get_serialized_sample_fallback()

    def _get_serialized_sample_fallback(self):
        """Return serialized dashboard from sample file when main data is missing or unreadable."""
        if self.sample_dashboard_file_path:
            sample_data = self._get_sample_dashboard()
            if sample_data:
                return json.dumps({
                    'snapshot': sample_data,
                    'revisions': [],
                    'default_currency': self.env['res.currency'].get_company_currency_for_spreadsheet(),
                    'translation_namespace': self._get_dashboard_translation_namespace(),
                })
        raise ValueError("No spreadsheet data available for this dashboard.")
