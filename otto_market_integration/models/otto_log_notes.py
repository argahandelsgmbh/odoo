from odoo import _, api, fields, models


class OttoLogNotes(models.Model):
    _name = 'otto.log.notes'
    _description = "Otto Log Notes"
    _rec_name = 'error'

    error = fields.Text('Error')