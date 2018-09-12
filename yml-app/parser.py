from lxml import etree
from lxml.etree import _Element as LxmlElement

INVALID_MSG = "Invalid XML format.\n"
SHOP_PATH = '/yml_catalog/shop/'


class ParserError(Exception):
    """ Exception in case of incorrect data in XML file """
    pass


class InvalidEntry(Exception):
    """ Exception in case of incorrect data in XML file """
    pass


class Offer:
    """ Represents offer """
    def __init__(self, lxml_element, id_map):

        self.oid = lxml_element.attrib['id']
        self.category_id = self._get_text(lxml_element, 'categoryId')
        self.category = id_map[self.category_id]
        self.price = self._get_text(lxml_element, 'price')
        self.name = self._get_text(lxml_element, 'name')

    def construct(self):
        entry = (
            'yml-offer_' + self.oid,
            (
                self.category,
                self.name,
                self.price,
            )
        )
        return entry

    def _get_text(self, element, tag):
        target = element.find(tag)
        if not isinstance(target, LxmlElement):
            raise InvalidEntry(
                INVALID_MSG
                + "offer Id{} doesn't have tag {}".format(self.oid, tag)
            )
        else:
            return target.text  # TODO validate text


class Parser:

    offers_tag = 'offers'
    categories_tag = 'categories'

    def __init__(self):
        pass

    def _find_in_path(self, xml, path, tag):
        offers = xml.xpath(path + tag)
        if not offers:
            raise ParserError(
                INVALID_MSG
                + "Tag <{}> not found".format(tag)
            )
        elif len(offers) > 1:
            raise ParserError(
                INVALID_MSG
                + "Multiple instanses of <{}> tag".format(tag)
            )
        else:
            return offers[0].iterchildren()

    def parse(self, xml_fname):
        try:
            xml = etree.parse(xml_fname)
        except OSError as err:
            raise ParserError(err)
        except etree.XMLSyntaxError as err:
            raise ParserError(err)

        offers = self._find_in_path(xml, SHOP_PATH, self.offers_tag)

        id_dict = dict()
        for element in self._find_in_path(xml, SHOP_PATH, self.categories_tag):
            id_dict[element.attrib['id']] = element.text

        offers = (Offer(element, id_dict) for element in offers)

        return offers
