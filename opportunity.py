#This file is part of opportunity_asterisk module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateTransition, Button

__all__ = ['SaleOpportunityAsterisk']


class SaleOpportunityAsterisk(Wizard):
    'Sale Opportunity Asterisk'
    __name__ = 'sale.opportunity.asterisk'

    start = StateView('sale.asterisk.result',
        'sale_asterisk.sale_asterisk_result_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Dial', 'dial', 'tryton-ok', default=True),
            ])
    dial = StateTransition()

    def default_start(self, fields):
        """
        This method searches phones of a sale order to show in the wizard.
        """
        opportunity = Transaction().context.get('active_id')
        Opportunity = Pool().get('sale.opportunity')
        opportunity = Opportunity(opportunity)
        mechanisms = []
        if opportunity:
            if opportunity.party:
                for mechanism in opportunity.party.contact_mechanisms:
                    if mechanism.type in ('phone', 'mobile'):
                        mechanisms.append(mechanism)
                if opportunity.party.relations:
                    for relationship in opportunity.party.relations:
                        for mechanism in relationship.to.contact_mechanisms:
                            if mechanism.type in ('phone', 'mobile'):
                                mechanisms.append(mechanism)
        mechanisms = list(set(mechanisms))
        return {
            'allowed_contacts_mechanisms': [m.id for m in mechanisms],
            'contact_mechanisms': mechanisms[0].id
            }

    def transition_dial(self, values=False):
        """
        Function called by the button 'Dial'
        """
        party = self.start.contact_mechanisms.party
        number = self.start.contact_mechanisms.value
        Asterisk = Pool().get('asterisk.configuration')
        Asterisk.dial(party, number)
        return 'end'
