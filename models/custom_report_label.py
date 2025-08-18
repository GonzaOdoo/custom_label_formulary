# models/label_wizard.py

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
class LabelWizard(models.TransientModel):
    _name = 'custom.client.label.wizard'
    _description = 'Asistente para imprimir etiquetas personalizadas'

    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    partner_invoice_id = fields.Many2one('res.partner', string='Facturar a')
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    component_id = fields.Many2one(
        'product.product',
        string='Componente',
        domain="[('id', 'in', available_component_ids)]"  # Filtrar por componentes del BOM
    )
    quantity = fields.Integer('Cantidad', default=1, required=True)
    ref = fields.Char('Referencia')
    origin = fields.Char('Pedido')
    date_order = fields.Datetime('Fecha de pedido', default=lambda self: fields.Datetime.now())
    x_studio_zona = fields.Char('Zona', compute='_compute_zona', store=True, readonly=False)
    x_studio_cliente_final = fields.Char('Cliente Final', default='CLIENTE FINAL')
    available_component_ids = fields.Many2many('product.product', string='Componentes disponibles', compute='_compute_available_components')

    @api.depends('partner_id')
    def _compute_zona(self):
        for rec in self:
            rec.x_studio_zona = rec.partner_id.x_studio_zona or ''

    def action_print_label(self):
        self.ensure_one()
        _logger.info(self.partner_id.id)
        date_order_formatted = self.date_order.strftime('%d/%m/%Y') if self.date_order else 'N/A'
        return {
            'type': 'ir.actions.report',
            'report_name': 'mostrar_info_en_lotes.studio_report_document_custom',
            'report_type': 'qweb-pdf',
            'data': {
                'doc_model': 'custom.client.label.wizard',
                'item_ids': self.id,
                'partner_id': self.partner_id.id,
                'partner_invoice_id': self.partner_invoice_id.id,
                'product_id': self.product_id.id,
                'component_id':self.component_id.id,
                'quantity': self.quantity,
                'origin': self.origin,
                'ref':self.ref,
                'date_order': date_order_formatted,
                'x_studio_zona': self.x_studio_zona,
                'x_studio_cliente_final': self.x_studio_cliente_final,
            },
            'context': {
                'active_model': 'custom.client.label.wizard',
                'active_id': self.id,
            }
        }

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Cuando cambia el producto, actualiza los componentes disponibles"""
        if self.product_id:
            # Buscar BOMs asociados al producto terminado
            bom = self.env['mrp.bom'].search([
                '|',
                ('product_id', '=', self.product_id.id),
                ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)
            ], limit=1)

            if bom:
                # Obtener todos los productos de las líneas del BOM
                components = bom.bom_line_ids.product_id
                self.available_component_ids = components
                # No forzamos component_id, pero el dominio ya filtra
            else:
                self.available_component_ids = []
                self.component_id = False
        else:
            self.available_component_ids = []
            self.component_id = False

    @api.depends('product_id')
    def _compute_available_components(self):
        """Campo computado necesario para el dominio"""
        for rec in self:
            if rec.product_id:
                bom = rec.env['mrp.bom'].search([
                    '|',
                    ('product_id', '=', rec.product_id.id),
                    ('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)
                ], limit=1)
                if bom:
                    rec.available_component_ids = bom.bom_line_ids.product_id
                else:
                    rec.available_component_ids = []
            else:
                rec.available_component_ids = []