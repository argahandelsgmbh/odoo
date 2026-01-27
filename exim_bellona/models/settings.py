from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
import requests
import json
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import AccessError
import logging
from requests.exceptions import RequestException
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)

class Credentials(models.Model):
    _name = 'bellona.credentials'
    _description = "Bellona Credentials"
    _rec_name = 'token'

    username = fields.Char('Username')
    password = fields.Char('Password')
    token = fields.Char('Token', copy=False)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    active = fields.Boolean('Active',default=True)
    state = fields.Selection([('active', 'Connected'), ('disconnect', 'Discounted')], string='Status',readonly=True)


    def getBellonaCredentials(self):
        currentCompany = self.env.company
        bellonaCredentials = self.env['bellona.credentials'].search([('company_id', '=', currentCompany.id),
                                                                       ('active', '=', True)])
        if len(bellonaCredentials.ids) > 1:
            raise ValidationError("Multiple Credentials are active for current company. Please select/active only one at a time.")
        elif len(bellonaCredentials.ids) == 0:
            raise ValidationError("No credential is assign to current company. Please go to Bellona->Credentials.")
        else:
            return bellonaCredentials.username, bellonaCredentials.password

    def connect_bellona_credentials(self):

        try:
            settings = self.env['res.config.settings']
            url = settings.getBaseURL() + "api/Account"
        
            username, password = self.getBellonaCredentials()
        
            payload = json.dumps({
                "userName": username,
                "password": password
            })
        
            headers = {
                'Content-Type': 'application/json'
            }
        
            currentCompany = self.env.company
            bellonaCredentials = self.env['bellona.credentials'].search(
                [
                    ('company_id', '=', currentCompany.id),
                    ('active', '=', True)
                ],
                limit=1
            )
        
            response = requests.post(
                url,
                headers=headers,
                data=payload,
                timeout=15
            )
        
            if response.status_code == 200:
                bellonaCredentials.state = 'active'
                response_data = response.json()
                self.write({
                    'token': response_data.get('value')
                })
            else:
                bellonaCredentials.state = 'disconnect'
                self.env["bellona.log.notes"].sudo().create({
                    'error': f"Credentials not working for {currentCompany.name}: "
                            f"{response.status_code} - {response.text}",
                })
        
        except RequestException as e:
            # Network / timeout / DNS / route issues
            if bellonaCredentials:
                bellonaCredentials.state = 'disconnect'
        
            _logger.exception("Bellona API connection error")
        
            self.env["bellona.log.notes"].sudo().create({
                'error': f"Bellona API connection failed for {currentCompany.name}: {str(e)}",
            })
        
        



    def ConnectBellonaScheduler(self):
        pass
        # bellona_company = self.env['bellona.credentials'].search([])
        # for company in bellona_company:
        #     settings = self.env['res.config.settings']
        #     url = settings.getBaseURL() + "api/Account"
        #     username=company.username
        #     password = company.password
        #     payload = json.dumps({
        #         "userName": username,
        #         "password": password
        #     })
        #     headers = {
        #         'Content-Type': 'application/json'
        #     }

        #     response = requests.request("POST", url, headers=headers, data=payload)
        #     if response.status_code == 200:
        #         company.state='active'
        #         response = json.loads(response.text)
        #         company.write({
        #             'token': response['value']
        #         })
        #     else:
        #         company.state = 'disconnect'
