import json

from odoo import models, fields, api, _, exceptions
from lxml.builder import E
from lxml import etree
from odoo.tools import config
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval, test_python_expr, time, datetime
from pytz import timezone
from random import *
BTN_STYLE = [('primary', 'Primary'),
             ('secondary', 'Secondary'),
             ('success', 'Success'),
             ('danger', 'Danger'),
             ('warning', 'Warning'),
             ('info', 'Info'),
             ('light', 'Light'),
             ('dark', 'Dark'),
             ('link', 'Link')]
BTN_COLORS = ['#71629e', '#ffffff', '#28a745', '#dc3545', '#ffac00', '#14a2b8', '#f8f9fa', '#343a40', '#ffffff']


class StageConstructor(models.Model):
    _name = 'stage.constructor'
    _rec_name = 'name'

    name = fields.Char(string="Buttonbox name", required=1)
    model_id = fields.Many2one('ir.model', 'Model')

    stage_id_domain = fields.Char(
    'Stage Domain Field',
    compute="_stage_id_domain",
    readonly=True,
    store=False,)
    stage_id = fields.Many2one('ir.model.fields', 'Stage Field')
    create_id = fields.Many2one('ir.model', 'Create Model')
    model = fields.Char(related='stage_id.relation')
    view_id = fields.Many2one('ir.ui.view', string='Extension View')
    stage_from = fields.Integer(string='From')
    stage_to = fields.Integer(string='to')
    button_type = fields.Selection([
        ('move', 'Move Stage'),
        ('create', 'Create Record'),
        ('voting', 'Voting'),
    ], string="Button Type")
    voter_ids = fields.One2many(
        'stage.voting', 'constructor_id', string='Voters')
    button_style = fields.Selection(BTN_STYLE, default='primary', string='Button style')
    color = fields.Char(compute="_compute_color")
    editing = fields.Selection([('on', 'On'), ('off', 'Off')], string="Editing", default='on')
    create_report = fields.Boolean(string='Create report')
    is_configured = fields.Boolean(string='Create report',readonly=1)
    reject_button = fields.Boolean(string='Add Reject Button')

    # @api.onchange('voter_ids')
    # def _onchange_department(self):
    #     for rec in self.voter_ids:
    #
    #         rec.employee_domain = json.dumps(
    #             [('position_id', '=', rec.employee_id.department_id)]
    #         )

    @api.onchange('model_id')
    def _stage_id_domain(self):
        for rec in self:
            rec.stage_id_domain = json.dumps(
                [('model_id.id', '=', rec.model_id.id), ('ttype', '=', 'many2one')]
            )

    @api.onchange('button_type')
    def _button_type(self):
        if self.button_type == 'create' and self.voter_ids:
            self.env['stage_voting'].search([('id', 'in', self.voter_ids)]).write({
                'eds_type': False
            })

    def api_move_project(self, model_id):
        self.ensure_one()
        inmodel = self.env[self.model_id.model].browse(model_id)
        if inmodel and inmodel["{}".format(self.stage_id.name)].id == self.stage_from:
            there=inmodel.write({
                'stage_id':self.stage_to
            })
            print(there)
        else:
            return {'warning': {
                'title': _("Warning"),
                'message': _(
                    "There some error, maybe stage is None or stage moved already by user")
            }}

    def api_vote_project(self):
        print(self)



    def action_archive(self):
        res = super(StageConstructor, self).action_archive()
        # Untick "Is Config?"
        # Delete view
        for r in self:
            r = r.sudo()
            vals = {
                'is_configured': False,
            }
            view = None
            if r.view_id:
                vals.update({'view_id': False})
                view = r.view_id
            r.write(vals)
            if view:
                # search
                args = [('view_id', '=', view.id),
                        ('id', '!=', r.id)]
                exist = self.search(args, limit=1)
                if not exist:
                    view.unlink()
        return res

    def create_compute_field(self, f_name, model_id):
        ResField = self.env['ir.model.fields']
        compute_f = ResField._get(self.model_id.model, f_name)
        if self.stage_id:
            compute_val = self.get_compute_val(self.stage_id.name,f_name)
            if not compute_f:
                f_vals = {
                    'name': f_name,
                    'field_description': f_name,
                    'ttype': 'char',
                    'copied': False,
                    'store': True,
                    'model_id': model_id,
                    'depends': self.stage_id.name,
                    'compute': compute_val
                    }
                ResField.create(f_vals)
                print(f_vals,'i have created')
            else:
                # Update compute function
                compute_f.write({'compute': compute_val})

    def get_compute_val(self,stage_id_name,f_name):
            vals = """
for rec in self:
    stages = self.env['stage.constructor'].search([('model_id.model', '=', rec._name), ('stage_from', '=', rec.%s.id)])
    if stages:
        routes = []
        for stage in stages:
            if stage.create_id:
                routes += [{
                    "id": stage.id,
                    "btn_type": stage.button_type,
                    "name": stage.name,
                    "btn_style": stage.button_style,
                    "stage_to": stage.stage_to,
                    "view_name": stage.model_id.model,
                    "create_id": stage.create_id.model,
                }]
            else:
                routes += [{
                    "id": stage.id,
                    "btn_type": stage.button_type,
                    "name": stage.name,
                    "btn_style": stage.button_style,
                    "stage_to": stage.stage_to,
                    "view_name": stage.model_id.model,
                }]
                if stage.reject_button:
                    routes += [{
                        "id": stage.id,
                        "btn_type": stage.button_type,
                        "name": stage.name,
                        "btn_style": stage.button_style,
                        "stage_to": stage.stage_to,
                        "view_name": stage.model_id.model,
                        "reject_button": "True",
                    }]
                else:
                    pass
        rec['%s'] = {'routes':routes}
    else:
        rec['%s'] = False""" % (stage_id_name, f_name, f_name)

            return vals

    def create_compute_field_domain(self, f_name, model_id):
        ResField = self.env['ir.model.fields']
        compute_f = ResField._get(self.model_id.model, f_name)
        if self.stage_id:
            compute_val = self.get_compute_val_domain(f_name)
            if not compute_f:
                f_vals = {
                    'name': f_name,
                    'field_description': f_name,
                    'ttype': 'boolean',
                    'copied': False,
                    'store': True,
                    'model_id': model_id,
                    'depends': self.stage_id.name,
                    'compute': compute_val
                    }
                ResField.create(f_vals)
                print(f_vals,'i have created')
            else:
                # Update compute function
                compute_f.write({'compute': compute_val})

    def get_compute_val_domain(self, f_name):
        vals = """
for rec in self:
    if rec.x_stage_voting_ids:
        for voter in rec.x_stage_voting_ids:
            allowed_by_user = (
                voter.employee_id in self.env.user.employee_ids)
            if allowed_by_user:
                rec['%s']=True
            else:
                rec['%s']=False""" % (f_name, f_name)
        return vals

    def get_compute_m2m(self, stage_id_name, f_name):
        vals = """
for rec in self:
    stages = self.env['stage.constructor'].search([('model_id.model', '=', rec._name), ('stage_from', '=', rec.%s.id)])
    if stages:
        inmodel_approvers = []
        for stage in stages:
            approvers = self.env['stage.voting'].search([('constructor_id', '=', stage.id)])
            for approver in approvers:
                inmodel_approver=self.env['stage.voting.inmodel'].create({
                        'position_id': approver.position_id.id,
                        'employee_id': approver.employee_id.id,
                        'constructor_id': approver.constructor_id.id,
                        'sequence': approver.sequence,
                        'status': False,
                        'eds_type': approver.eds_type,
                    }).id
                inmodel_approvers.append(inmodel_approver)
        rec['%s'] = [(6, 0, inmodel_approvers)]
    else:
        rec['%s']=False""" % (stage_id_name, f_name,f_name)
        return vals

    def create_m2m_field(self, f_name, model_id):
        ResField = self.env['ir.model.fields']
        compute_val = self.get_compute_m2m(self.stage_id.name, f_name)
        field_id = ResField._get(self.model_id.model, f_name)
        if not field_id:
            f_vals = {
                'name': f_name,
                'field_description': f_name,
                'ttype': "many2many",
                'relation': "stage.voting.inmodel",
                'copied': False,
                'compute': compute_val,
                'readonly': True,
                'depends': self.stage_id.name,
                'store': True,
                'model_id': model_id}
            ResField.create(f_vals)
        else:
            # Update compute function
            field_id.write({'compute': compute_val})

    def get_default_view(self):
        view_id = self.env['ir.ui.view'].default_view(self.model_id.model, 'form')
        return view_id

    def get_existed_view(self):
        self.ensure_one()
        args = [('model_id', '=', self.model_id.model),
                ('view_id', '!=', False)]
        exist = self.search(args, limit=1)
        return exist.view_id

    def create_view(self, f_name, f_name4, f_name2):
        '''
        1. Find a base view
        2. Check if it has a header path already?
        3. If not, create new header path
        4. Insert 2 button inside the header path
            - Request Approval: if there is no request yet
            - View Approval: if already has some
        5 Find a base report view
        6 Insert Approvers list
        '''
        if self.view_id:
            return False
        existed_view = self.get_existed_view()
        if existed_view:
            self.view_id = existed_view
            return False
        IrView = self.env['ir.ui.view']
        model_id = self.env['ir.model']._get_id(self.model_id.model)
        view_id = self.get_default_view()
        if not view_id:
            raise Warning(_('This model has no form view !'))
        view_content = self.env[self.model_id.model]._fields_view_get(view_id)
        view_arch = etree.fromstring(view_content['arch'])
        node = IrView.locate_node(
            view_arch,
            E.xpath(expr="//form/header"),
        )
        # Searching for notebook in form view
        node_m2o = IrView.locate_node(
            view_arch,
            E.xpath(expr="//form/sheet/notebook"),
        )

        f_node2 = E.field(name=f_name2, invisible="1")
        f_node = E.field(
            name=f_name,
            attrs=str({'invisible': [(f_name2, '=', False)]}),
            widget="stage_btn_widget")
        div_node = E.div(f_node2,f_node,
            {'class': "stage_route_out_widget"},
        )
        # Creating one2many field xml
        f4_node = E.field(
            {'name': f_name4},
            E.tree(
                E.field(name='constructor_id'),
                E.field(name='position_id'),
                E.field(name='employee_id'),
                E.field(name='sequence'),
                E.field(name='status'),
                E.field(name='eds_type'),
            ))

        # Create header tag if there is not yet
        if node is None:
            header_node = E.header(
                div_node,
            )
            # find a sheet
            sheet_node = IrView.locate_node(
                view_arch,
                E.xpath(expr="//form/sheet"),
            )
            expr = "//form/sheet"
            position = "before"
            if sheet_node is None:
                expr = "//form"
                position = "inside"
            xml = E.xpath(
                header_node,
                expr=expr, position=position)
        else:
            xml0 = E.xpath(
                div_node,
                expr="//form/header", position="inside")
            xml = E.data(
                xml0,
            )
        # Create notebook if there is None
        if node_m2o is None:
            page_1 = E.page(
                f4_node,
                name="stage_voting_inmodel",
                string="Approver(s)",
            )
            notebook_1 = E.notebook(
                page_1
            )
            # find a sheet
            sheet_node = IrView.locate_node(
                view_arch,
                E.xpath(expr="//form/sheet"),
            )
            expr = "//form/sheet"
            position = "inside"
            xml_page = E.xpath(
                notebook_1,
                expr=expr, position=position)
            xml.append(xml_page)
        else:
            page_1 = E.page(
                f4_node,
                name="stage_voting_inmodel",
                string="Approver(s)",
            )
            xml3 = E.xpath(
                page_1,
                expr="//form/sheet/notebook", position="inside")
            xml.append(xml3)

        xml_content = etree.tostring(
            xml, pretty_print=True, encoding="unicode")
        new_view_name = 'stage_constructor_' + fields.Datetime.now().strftime(
            '%Y%m%d%H%M%S')
        new_view = IrView.create({
            'name': new_view_name,
            'model': self.model_id.model,
            'inherit_id': view_id,
            'arch': xml_content})
        self.view_id = new_view

    def action_configure(self):
        self.ensure_one()
        self = self.sudo()
        ResModel = self.env['ir.model']


        model_id = ResModel._get_id(self.model_id.model)

        # Create compute field
        compute_field = 'x_stage_constructor'
        self.create_compute_field(compute_field, model_id)
        # Create many2many field
        m2m_field = "x_stage_voting_ids"
        self.create_m2m_field(m2m_field, model_id)
        # Create compute field for domain of x_stage_constructor
        compute_field_domain = 'x_stage_constructor_domain'
        self.create_compute_field_domain(compute_field_domain, model_id)



        # create extension view
        self.create_view(compute_field,  m2m_field, compute_field_domain)
        self.is_configured = True

    def compute_color(self, button_style):
        for s, c in zip(BTN_STYLE, BTN_COLORS):
            if button_style == s[0]:
                return c

    @api.depends('button_style')
    def _compute_color(self):
        for rec in self:
            rec.color = self.compute_color(rec.button_style)