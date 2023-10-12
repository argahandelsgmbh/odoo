from odoo import _, api, fields, models


class IstikbalLogNotes(models.Model):
    _name = 'istikbal.log.notes'
    _description = "Istikbal Logs"
    _rec_name = 'error'

    error = fields.Text('Error')
    company_id = fields.Many2one('res.company', string='Company')