# Import modules
import os, requests, re, sys
import pandas as pd
import xml.etree.ElementTree as ET

# Define class
class DSD:
    def __init__(self, dataset_id):
        self.dataset_id = dataset_id
        self.lang = 'en'
        self.download_dsd()
        self.set_dsd()
        
    def download_dsd(self):
        datastructure = f'https://stats.oecd.org/restsdmx/sdmx.ashx/GetDataStructure/{self.dataset_id}'
        # Send request
        response = requests.get(datastructure)
        # Terminate program if there is no such dataset id
        if response.status_code!=200:
            print(f"There is no such an id ({self.dataset_id})! Look for available datasets in the 'id' attributes " \
                     f"of 'KeyFamily' tags on https://stats.oecd.org/restsdmx/sdmx.ashx/GetDataStructure/all. " \
                     "When you find one, run the program again with a correct dataset id.")
            sys.exit()
        dsd = response.text
        # Fixing XML format
        regex = re.compile(r"<message:Structure(.*?)>")
        m = re.search(regex, dsd)
        del_part = m.group(1)
        dsd_fixed = dsd.replace(r'{}'.format(del_part), "")
        dsd_fixed = re.sub(r' xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message"', "", dsd_fixed)
        dsd_fixed = dsd_fixed.replace('message:', '')
        dsd_fixed = dsd_fixed.replace('xml:lang', 'lang')
        # Get formatted dsd
        self.dsd_xml = dsd_fixed
        
    def set_dsd(self):
        # Inner functions
        # Choose specific child element
        def child_el(el, el_tag = None):
            for i in el:
                if (i.get('lang') == self.lang) and not el_tag:
                    return i
                elif (i.get('lang') == self.lang) and el_tag:
                    if el_tag == i.tag:
                        return i
        # Add element info to dictionary
        def add_el_to_dic(el, el_tag = None):
            # Add attributes
            def add_attrs(a, e):    
                dic = {}
                for attr in a.keys():
                    dic[attr] = a[attr]
                if el.text:
                    try:
                        dic[e.tag] = attrs[e.text]
                    except:
                        pass
                if e.tag in ['Code']:
                    dic['description'] = child_el(e).text
                return dic
            #Process element
            attrs = el.attrib
            # Do not process element if it does not have desired tag name
            if el_tag:
                if el_tag == el.tag:
                    return add_attrs(attrs, el)
                else:
                    pass
            # Process element if tag name is not specified
            else:
                return add_attrs(attrs, el)
        # Add elements info to dictionary
        def add_els_to_dic(p_el, tags=None, el_tag = None):
            arr = []
            for el in p_el:
                dic = add_el_to_dic(el, el_tag)
                if dic:
                    if tags:
                        dic[tags] = el.tag
                    arr.append(dic)
            return arr
        # Define dimensions, attributes, and time dimension
        def transform(dic):
            list_ = []
            key = dic['conceptRef']
            val = dic.get('codes', None)
            if val is None:
                list_ = [key,val]
            else:
                val_arr = []
                for i in val:
                    val_arr.append(i['value'])
                list_ = [key,val_arr]
            return list_
                
        
        # Define future attributes
        self.agency_id = ''
        self.description = ''
        self.concepts = {}
        self.dimensions = []
        self.attributes = []
        self.time_dimension = []
        
        # Get xml root
        root = ET.fromstring(self.dsd_xml)
        # Key family info
        key_family = root.find('./KeyFamilies/KeyFamily')
        self.agency_id = key_family.attrib['agencyID']
        key_family_desc = root.findall("./KeyFamilies/KeyFamily/")
        self.description = child_el(key_family_desc).text
        # Add a dictionary with concepts and their codes
        concepts = add_els_to_dic(root.findall('./KeyFamilies/KeyFamily/Components/'), tags='concept')
        self.concepts = concepts
        # Add codes to concepts
        for el in root.findall('./CodeLists/'):
            for concept_i in range(len(self.concepts)):
                try:
                    if el.get('id') == self.concepts[concept_i]['codelist']:
                        codes = add_els_to_dic(el, el_tag = 'Code')
                        self.concepts[concept_i]['codes'] = codes
                except:
                    continue
        # Add description to concepts
        for el in root.findall('./Concepts/'):
            for concept_i in range(len(self.concepts)):
                try:
                    if el.get('id') == self.concepts[concept_i]['conceptRef']:
                        desc = child_el(el).text
                        self.concepts[concept_i]['description'] = desc
                except:
                    continue       
        # Define dimensions, attributes, and time dimension
        for i in self.concepts:
            concept = i['concept']
            if concept == 'Dimension':
                self.dimensions.append(transform(i))
            elif concept == 'Attribute':
                self.attributes.append(transform(i))
            elif concept == 'TimeDimension':
                self.time_dimension.append(transform(i))
    
    # dsd to string
    def to_string(self):
        print(f"\nDSD - {self.dataset_id}\nDSD name - {self.description}\nDSD agency - {self.agency_id}\n\nConcepts:")
        just_num = 30
        for i in range(len(self.concepts)):
            concept_type = self.concepts[i]['concept']
            concept_ref = self.concepts[i]['conceptRef']
            desc = self.concepts[i]['description']
            code_num = str(len(self.concepts[i].get('codes', [])))
            print('{}{}{}{}'.format(concept_type.ljust(just_num), concept_ref.ljust(just_num), desc.ljust(just_num), code_num.ljust(just_num)))