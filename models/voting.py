import json

from odoo import models, fields, api, _, exceptions


class Voting(models.Model):
    _name = 'stage.voting'
    _description = 'Project Voting'

    position_id = fields.Many2one(
        'hr.department', string='Position')
    employee_id = fields.Many2one(
        'hr.employee', string='Employee')
    employee_domain = fields.Char(
        string='Employee Domain',
        readonly=True,
        store=False
    )
    constructor_id = fields.Many2one(
        'stage.constructor', string='Constructor')
    sequence = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
    ], string="Sequence")
    eds_type = fields.Selection([
        ('without', 'Without Signing'),
        ('eds', 'Signing EDS'),
        ('qr', 'Signing QR'),
    ], string="Signing")


class VotingInModel(models.Model):
    _name = 'stage.voting.inmodel'
    _description = 'Project Voting In Model'

    position_id = fields.Many2one(
        'hr.department', string='Position')
    employee_id = fields.Many2one(
        'hr.employee', string='Voter')
    constructor_id = fields.Many2one(
        'stage.constructor', string='Constructor')
    sequence = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
    ], string="Sequence")
    status = fields.Boolean('Status', default=False)
    eds_type = fields.Selection([
        ('without', 'Without Signing'),
        ('eds', 'Signing EDS'),
        ('qr', 'Signing QR'),
    ], string="Signing")