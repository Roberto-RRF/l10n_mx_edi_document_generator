from odoo import models, api, fields
from odoo.exceptions import UserError
class AccountMove(models.Model):
    _inherit = 'account.move'


    def write(self, vals):
        """
        Override the write method to listen for changes in attachment_ids.
        """
        res = super(AccountMove, self).write(vals)

        if 'attachment_ids' in vals:
            for record in self:
                raise UserError("In write")
                if not record.l10n_mx_edi_document_ids and record.move_type == 'in_invoice':

                    # Extract UUID and create EDI document if applicable
                    uuid = record._extract_uuid_from_attachment()
                    if uuid:
                        record.create_edi_document_from_attachment(uuid)

        return res


    def create_edi_document_from_attatchment(self):
        edi = self.env['l10n_mx_edi.document']
        edi_content = self.attachment_ids.filtered(lambda m: m.mimetype == 'application/xml')
        print("In create_edi_document_from_attatchment")
        data = self.env['l10n_mx_edi.document']._decode_cfdi_attachment(edi_content.raw)
        print(data['uuid'])
        print("AQUI \n\n\n")
        if edi_content:
            edi_data = {
                'state' : 'invoice_sent',
                'datetime': fields.Datetime.now(),
                'attachment_uuid':data['uuid'],
                'attachment_id':edi_content.id,
                'move_id': self.id,
            }
            new_edi_doc = edi.create(edi_data)

            # Asociar las facturas
            new_edi_doc.invoice_ids = [(6, 0, [self.id])] 