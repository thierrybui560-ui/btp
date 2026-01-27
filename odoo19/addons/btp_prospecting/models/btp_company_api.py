# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    _logger.warning('requests library not available. API enrichment will be disabled.')


class BtpCompanyApiService(models.AbstractModel):
    """Service for enriching company data from external APIs (INSEE, Pappers, Infogreffe)"""
    _name = 'btp.company.api.service'
    _description = 'BTP Company API Service'

    def enrich_from_pappers(self, siren):
        """
        Enrich company data from Pappers API
        Note: Requires API key in system parameters
        """
        if not REQUESTS_AVAILABLE:
            _logger.warning('requests library not available')
            return {}
        
        api_key = self.env['ir.config_parameter'].sudo().get_param('btp_prospecting.pappers_api_key', False)
        if not api_key:
            _logger.warning('Pappers API key not configured')
            return {}
        
        try:
            url = f'https://api.pappers.fr/v2/entreprise'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            params = {'siren': siren}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('entreprise'):
                return self._parse_pappers_data(data['entreprise'])
        except requests.exceptions.RequestException as e:
            _logger.error(f'Pappers API error: {e}')
        except Exception as e:
            _logger.error(f'Error parsing Pappers data: {e}')
        
        return {}
    
    def enrich_from_insee(self, siren):
        """
        Enrich company data from INSEE API
        """
        if not REQUESTS_AVAILABLE:
            _logger.warning('requests library not available')
            return {}
        
        try:
            url = f'https://api.insee.fr/entreprises/sirene/v3/siren/{siren}'
            headers = {
                'Accept': 'application/json'
            }
            api_key = self.env['ir.config_parameter'].sudo().get_param('btp_prospecting.insee_api_key', False)
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('uniteLegale'):
                return self._parse_insee_data(data['uniteLegale'])
        except requests.exceptions.RequestException as e:
            _logger.error(f'INSEE API error: {e}')
        except Exception as e:
            _logger.error(f'Error parsing INSEE data: {e}')
        
        return {}
    
    def enrich_from_infogreffe(self, siren):
        """
        Enrich company data from Infogreffe API
        Note: May require authentication
        """
        if not REQUESTS_AVAILABLE:
            _logger.warning('requests library not available')
            return {}

        api_key = self.env['ir.config_parameter'].sudo().get_param('btp_prospecting.infogreffe_api_key', False)
        api_url = self.env['ir.config_parameter'].sudo().get_param('btp_prospecting.infogreffe_api_url', False)
        if not api_url:
            _logger.warning('Infogreffe API URL not configured')
            return {}

        headers = {'Accept': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        try:
            response = requests.get(api_url, headers=headers, params={'siren': siren}, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Minimal parsing; adjust mapping to your Infogreffe response format
            result = {}
            if data.get('name'):
                result['name'] = data['name']
            if data.get('siren'):
                result['siren'] = str(data['siren']).zfill(9)
            if data.get('siret'):
                result['siret'] = str(data['siret']).zfill(14)
            if data.get('naf'):
                result['naf_code'] = data['naf']
            if data.get('legal_form'):
                result['legal_form'] = data['legal_form']
            if data.get('capital'):
                try:
                    result['capital'] = float(data['capital'])
                except (ValueError, TypeError):
                    pass
            if data.get('address'):
                result['street'] = data['address']
            if data.get('zip'):
                result['zip'] = data['zip']
            if data.get('city'):
                result['city'] = data['city']

            return result
        except requests.exceptions.RequestException as e:
            _logger.error(f'Infogreffe API error: {e}')
        except Exception as e:
            _logger.error(f'Error parsing Infogreffe data: {e}')

        return {}
    
    def _parse_pappers_data(self, data):
        """Parse Pappers API response"""
        result = {}
        
        # Company name
        if data.get('nom_entreprise'):
            result['name'] = data['nom_entreprise']
        elif data.get('denomination'):
            result['name'] = data['denomination']
        
        # SIREN/SIRET
        if data.get('siren'):
            result['siren'] = str(data['siren']).zfill(9)
        if data.get('siret_siege'):
            result['siret'] = str(data['siret_siege']).zfill(14)
        
        # Address
        if data.get('siege'):
            siege = data['siege']
            address_parts = []
            if siege.get('numero_voie'):
                address_parts.append(str(siege['numero_voie']))
            if siege.get('type_voie'):
                address_parts.append(siege['type_voie'])
            if siege.get('libelle_voie'):
                address_parts.append(siege['libelle_voie'])
            if address_parts:
                result['street'] = ' '.join(address_parts)
            if siege.get('code_postal'):
                result['zip'] = str(siege['code_postal']).zfill(5)
            if siege.get('ville'):
                result['city'] = siege['ville']
        
        # NAF code
        if data.get('code_naf'):
            result['naf_code'] = data['code_naf']
        
        # Legal form
        if data.get('forme_juridique'):
            result['legal_form'] = data['forme_juridique']
        
        # Capital
        if data.get('capital'):
            try:
                result['capital'] = float(data['capital'])
            except (ValueError, TypeError):
                pass
        
        return result
    
    def _parse_insee_data(self, data):
        """Parse INSEE API response"""
        result = {}
        
        # Company name
        if data.get('denominationUniteLegale'):
            result['name'] = data['denominationUniteLegale']
        elif data.get('nomUniteLegale'):
            result['name'] = data['nomUniteLegale']
        
        # SIREN
        if data.get('siren'):
            result['siren'] = str(data['siren']).zfill(9)
        
        # Address (from periodesUniteLegale)
        if data.get('periodesUniteLegale') and len(data['periodesUniteLegale']) > 0:
            periode = data['periodesUniteLegale'][0]
            if periode.get('adresseEtablissement'):
                adresse = periode['adresseEtablissement']
                address_parts = []
                if adresse.get('numeroVoieEtablissement'):
                    address_parts.append(str(adresse['numeroVoieEtablissement']))
                if adresse.get('typeVoieEtablissement'):
                    address_parts.append(adresse['typeVoieEtablissement'])
                if adresse.get('libelleVoieEtablissement'):
                    address_parts.append(adresse['libelleVoieEtablissement'])
                if address_parts:
                    result['street'] = ' '.join(address_parts)
                if adresse.get('codePostalEtablissement'):
                    result['zip'] = str(adresse['codePostalEtablissement']).zfill(5)
                if adresse.get('libelleCommuneEtablissement'):
                    result['city'] = adresse['libelleCommuneEtablissement']
        
        # NAF code
        if data.get('activitePrincipaleUniteLegale'):
            result['naf_code'] = data['activitePrincipaleUniteLegale']
        
        # Legal form
        if data.get('categorieJuridiqueUniteLegale'):
            result['legal_form'] = data['categorieJuridiqueUniteLegale']
        
        return result
    
    def enrich_company(self, siren, source='pappers'):
        """
        Main method to enrich company data
        Tries multiple sources if first fails
        """
        if source == 'pappers':
            data = self.enrich_from_pappers(siren)
            if data:
                return data, 'pappers'
            # Fallback to INSEE
            data = self.enrich_from_insee(siren)
            if data:
                return data, 'insee'
        elif source == 'insee':
            data = self.enrich_from_insee(siren)
            if data:
                return data, 'insee'
            # Fallback to Pappers
            data = self.enrich_from_pappers(siren)
            if data:
                return data, 'pappers'
        
        return {}, 'manual'


# API service is used by res.partner model (see res_partner.py)

