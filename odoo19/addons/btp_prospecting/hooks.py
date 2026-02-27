# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.

def post_init_hook_qse_attachment_migration(cr, registry):
    """
    Migrate QHSE incident attachments from M2M relation table to standard
    ir.attachment res_model/res_id so they appear in the computed field
    and chatter drag-and-drop can be used for new uploads.
    """
    from odoo import SUPERUSER_ID
    table = 'btp_qse_incident_attachment_rel'
    cr.execute("""
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = current_schema() AND table_name = %s
    """, (table,))
    if not cr.rowcount:
        return
    cr.execute("""
        UPDATE ir_attachment a
        SET res_model = 'btp.qse.incident', res_id = r.incident_id
        FROM btp_qse_incident_attachment_rel r
        WHERE a.id = r.attachment_id
          AND (a.res_model IS NULL OR a.res_model != 'btp.qse.incident' OR a.res_id != r.incident_id)
    """)
