#
# OpenDict
# Copyright (c) 2003-2005 Martynas Jocius <mjoc@akl.lt>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your opinion) any later version.
#
# This program is distributed in the hope that will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MECHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more detals.
#
# You shoud have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# 02111-1307 USA
#

import xml.dom.minidom


class RegisterConfigGenerator:
    """Class for generating register configuration files"""

    def generate(self, **args):
        """Generate config XML object"""

        doc = xml.dom.minidom.Document()

        registerElement = doc.createElement("register")
        doc.appendChild(registerElement)

        # Format element
        formatElement = doc.createElement("format")
        registerElement.appendChild(formatElement)
        formatElement.appendChild(doc.createTextNode(args.get('format')))

        # Name element
        nameElement = doc.createElement("name")
        registerElement.appendChild(nameElement)
        nameElement.appendChild(doc.createTextNode(args.get('name')))

        # Path element
        pathElement = doc.createElement("path")
        registerElement.appendChild(pathElement)
        pathElement.appendChild(doc.createTextNode(args.get('path')))

        # MD5 element
        md5Element = doc.createElement("md5")
        registerElement.appendChild(md5Element)
        md5Element.appendChild(doc.createTextNode(args.get('md5')))

        # Encoding element
        encodingElement = doc.createElement("encoding")
        registerElement.appendChild(encodingElement)
        encodingElement.appendChild(doc.createTextNode(args.get('encoding')))

        return doc
    

def generateRegisterConfig(**args):
    """Generate configuration and return XML string"""

    generator = RegisterConfigGenerator()
    doc = generator.generate(**args)
    xmlData = doc.toxml()

    return xmlData


class RegisterConfigParser:
    """Parse register configuration"""

    def parse(self, xmlData):
        """Parse XML data"""

        doc = xml.dom.minidom.parseString(xmlData)
        name = None
        format = None
        path = None
        md5 = None
        encoding = None

        registers = doc.getElementsByTagName('register')
        if len(registers) == 0:
            raise "Invalid configuration"

        registerElement = registers[0]
        
        for nameElement in registerElement.getElementsByTagName('name'):
            for node in nameElement.childNodes:
                name = node.data

        for formatElement in registerElement.getElementsByTagName('format'):
            for node in formatElement.childNodes:
                format = node.data

        for pathElement in registerElement.getElementsByTagName('path'):
            for node in pathElement.childNodes:
                path = node.data

        for md5Element in registerElement.getElementsByTagName('md5'):
            for node in md5Element.childNodes:
                md5 = node.data

        for encodingElement in \
                registerElement.getElementsByTagName('encoding'):
            for node in encodingElement.childNodes:
                encoding = node.data

        result = {}
        result['name'] = name
        result['format'] = format
        result['path'] = path
        result['md5'] = md5
        result['encoding'] = encoding

        return result


def parseRegisterConfig(configPath):
    """Parse configuration file and return data dictionary"""

    parser = RegisterConfigParser()
    fd = open(configPath)
    xmlData = fd.read()
    fd.close()
    data = parser.parse(xmlData)

    return data
    

if __name__ == "__main__":
    print generateRegisterConfig(name='Test', format='Nonsense',
                                 path='/home/mjoc/xxx/',
                                 md5='34kj34lk5j3lkj345',
                                 encoding='UTF-8')

    print parseRegisterConfig('/home/mjoc/config.xml')
