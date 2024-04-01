from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
import json
import requests
import base64
import time
from datetime import datetime, timedelta


class Credentials(models.Model):
    _name = 'otto.credentials'
    _description = "otto.credentials"

    otto_username = fields.Char(string='Username')
    otto_password = fields.Char(string='Password')
    otto_credentials_type = fields.Selection([('https://sandbox.api.otto.market', 'Sandbox'),
                                              ('https://api.otto.market', 'Production')],
                                             string="Credentials Type", default='https://sandbox.api.otto.market')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    active = fields.Boolean('Active',default=True)

    def auto_otto_generate_token(self):
        self.otto_generate_token(True)

    def otto_generate_token(self, auto=False):
        """
        Generate OTTO Token for API
        :return:
        """
        try:
            ottoCredentials = self.env['otto.credentials'].search([],limit=1)
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            otto_username = ottoCredentials.otto_username
            otto_password = ottoCredentials.otto_password
            otto_credentials_type = ottoCredentials.otto_credentials_type
            url = otto_credentials_type + "/v1/token"

            payload = 'username=%s&password=%s&grant_type=password&client_id=token-otto-api' % (otto_username, otto_password)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == 200:
                token_response = json.loads(response.text)
                IrConfigParameter.set_param('otto_market_integration.otto_token', token_response['access_token'])
                IrConfigParameter.set_param('otto_market_integration.otto_refresh_token', token_response['refresh_token'])
                IrConfigParameter.set_param('otto_market_integration.otto_expires_in', int(round(time.time() * 1000)))
                if not auto:
                    # return self.action_of_button('Successful', 'Successfully Connected to Otto Market')
                    otto_log = self.env['otto.log.notes'].sudo().create({'error': "Successfully Connected to Otto Market"})
            else:
                token_response = json.loads(response.text)
                if not auto:
                    # return self.action_of_button('Failed', token_response['error_description'])
                    otto_log = self.env['otto.log.notes'].sudo().create({
                        'error': "Generating token Error " + str(token_response['error_description']),
                    })
        except Exception as e:
            otto_log = self.env['otto.log.notes'].create({
                'error': "Generating token Error " + str(e),
            })

    def action_of_button(self, name, message):
        message_id = self.env['message.wizard'].create({
            'text': message,
        })
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'res_id': message_id.id,
            'target': 'new',
        }
