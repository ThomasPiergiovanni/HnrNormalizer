"""Test normalizer manager  module.
"""
from django.test import TestCase

from normalizer.management.engine.normalizer_manager import NormalizerManager
from normalizer.tests.unit.management.clients.test_csv_manager import CsvManagerTest


class NormalizerManagerTest(TestCase):
    """Test normalizer manager class.
    """
    def setUp(self):
        self.manager =NormalizerManager()
        self.data = None
        self.ref_address = None
    
    @classmethod
    def emulate_raw_data(cls):
        raw_data = [
            ['id', 'adresse'],
            ['1', '12 rue Ledru-Rollin'],
            ['2', '65 rue des Bas Rogers'],
            ['46', '51 allée de la pépinière'],
            ['3', '28 rue victor hugo']
        ]
        return raw_data
    
    @classmethod
    def emulate_address_list(cls):
        address_list = [
            {
                'id': '1',
                'address': '51 allée de la pépinière'
            },
            {
                'id': '4',
                'address': '51 allée de la pépinière 92500 SUresnes'
            },
            {
                'id': '5',
                'address': '51 allée de la pépinière 92500SUresnes'
            },
            {
                'id': '6',
                'address': '51 allée de la pépinière92500SUresnes'
            }
        ]
        return address_list

    def test_get_raw_data(self):
        csv_manager_test = CsvManagerTest()
        csv_manager_test.emulate_imported_data()
        self.manager._NormalizerManager__get_raw_data()
        self.assertEqual(
            self.manager.raw_data[2],
            csv_manager_test.imported_data[2]
        )
    
    def test_set_attributes(self):
        self.manager.raw_data = self.emulate_raw_data()
        self.manager._NormalizerManager__set_attributes()
        self.assertEqual(self.manager.address_list[0]['id'], '1')
        self.assertEqual(
            self.manager.address_list[2]['address'],
            '51 allée de la pépinière'
        )

    def test_remove_zip(self):
        self.manager.address_list = self.emulate_address_list()
        self.manager._NormalizerManager__remove_zip()
        self.assertEqual(
            self.manager.address_list[0]['address'],
            '51 allée de la pépinière' 
        )
        self.assertEqual(
            self.manager.address_list[1]['address'],
            '51 allée de la pépinière  SUresnes' 
        )
        self.assertEqual(
            self.manager.address_list[2]['address'],
            '51 allée de la pépinière SUresnes' 
        )
        self.assertEqual(
            self.manager.address_list[3]['address'],
            '51 allée de la pépinièreSUresnes' 
        )
    
    def test_remove_unwanted_characters(self):
        self.manager.address_list = [
            {
                'id': '1',
                'address': '51, allée! de la pépinière'
            }
        ]
        self.manager._NormalizerManager__remove_unwanted_characters()
        self.assertEqual(
            self.manager.address_list[0]['address'],
            '51  allée  de la pépinière' 
        )
    
    def test_lower_string(self):
        self.manager.address_list = self.emulate_address_list()
        self.manager._NormalizerManager__lower_string()
        self.assertEqual(
            self.manager.address_list[1]['address'],
            '51 allée de la pépinière 92500 suresnes' 
        )

    def test_remove_accent(self):
        self.manager.address_list = self.emulate_address_list()
        self.manager._NormalizerManager__remove_accent()
        self.assertEqual(
            self.manager.address_list[0]['address'],
            '51 allee de la pepiniere' 
        )

    def test_remove_city_name(self):
        self.manager.address_list = [
            {
                'id': '1',
                'address': '51 allée de la pépinière 92500 suresnes'
            }
        ]
        self.manager._NormalizerManager__remove_city_name()
        self.assertEqual(
            self.manager.address_list[0]['address'],
            '51 allée de la pépinière 92500 ' 
        )


    def test_strip_and_trim(self):
        self.manager.address_list = [
            {
                'id': '1',
                'address': '51 allée de la  pépinière 92500 suresnes !'
            },
            {
                'id': '2',
                'address': ' 51 allée     de la  pépinière 92500 suresnes!'
            }
        ]
        self.manager._NormalizerManager__strip_and_trim()
        self.assertEqual(
            self.manager.address_list[0]['address'],
            '51 allée de la pépinière 92500 suresnes' 
        )
        self.assertEqual(
            self.manager.address_list[1]['address'],
            '51 allée de la pépinière 92500 suresnes' 
        )
    def test_set_adress_component(self):
        self.manager.address_list = [
            {
                'id': '1',
                'address': '51 allée de la pépinière 92500 suresnes'
            }
        ]
        self.manager._NormalizerManager__set_address_components()
        self.assertEqual(self.manager.address_list[0]['comp_1'], '51')
        self.assertEqual(self.manager.address_list[0]['comp_2'], 'allée')
        self.assertEqual(self.manager.address_list[0]['comp_3'], 'de')
        self.assertEqual(self.manager.address_list[0]['comp_4'], 'la')
        self.assertEqual(self.manager.address_list[0]['comp_5'], 'pépinière')
        self.assertEqual(self.manager.address_list[0]['comp_6'], '92500')
        self.assertEqual(self.manager.address_list[0]['comp_7'], 'suresnes')
    
    def test_remove_incorrect_prefix(self):
        self.manager.address_list = [
            {
                'id': '1',
                'address': '51 allée de la pépinière 92500 suresnes',
                'comp_1': '51',
                'comp_2': 'av',
                'comp_3': 'de',
                'comp_4': 'la',
                'comp_5': 'pépinière',
                'comp_6': '92500',
                'comp_7': 'suresnes'
            }
        ]
        self.manager._NormalizerManager__remove_incorrect_prefix()
        self.assertEqual(self.manager.address_list[0]['comp_1'], '51')
        self.assertEqual(self.manager.address_list[0]['comp_2'], 'avenue')
    

    def test_loop_prefix(self):
        item = {
            'id': '1',
            'address': '51 allée de la pépinière 92500 suresnes',
            'comp_1': '51',
            'comp_2': 'av',
            'comp_3': 'de',
            'comp_4': 'la',
            'comp_5': 'pépinière',
            'comp_6': '92500',
            'comp_7': 'suresnes'
        }
        component = item['comp_2']
        component_name = 'comp_2'
        perfix_list = [
            {
                'correct_name': "allee",
                'incomformities': ["ALL", "All", "all"]
            },
            {
                'correct_name': "avenue",
                'incomformities': ["AV", "Av", "av"]
            }
        ]
        method_output = self.manager._NormalizerManager__loop_prefix_dict(
            item, component, component_name, perfix_list
        )
        self.assertEqual(method_output['comp_2'], 'avenue')
    
