#
# OpenDict
# Copyright (c) 2003-2006 Martynas Jocius <martynas.jocius@idiles.com>
# Copyright (c) 2007 IDILES SYSTEMS, UAB <support@idiles.com>
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
import xml.dom.ext

from lib import meta


def _textData(element):
    """Return text data from given XML element"""

    text = ''
    for node in element.childNodes:
        text = node.data

    return text


class RegisterConfigGenerator:
    """Class for generating register configuration files"""

    def generate(self, **args):
        """Generate config XML object"""

        doc = xml.dom.minidom.Document()

        registerElement = doc.createElement('plain-dictionary')
        doc.appendChild(registerElement)

        # Format element
        formatElement = doc.createElement('format')
        registerElement.appendChild(formatElement)
        formatElement.appendChild(doc.createTextNode(args.get('format')))

        # Name element
        nameElement = doc.createElement('name')
        registerElement.appendChild(nameElement)
        nameElement.appendChild(doc.createTextNode(args.get('name')))

        # Version element
        versionElement = doc.createElement('version')
        registerElement.appendChild(versionElement)
        versionElement.appendChild(doc.createTextNode(args.get('version') \
                                                      or ''))

        # Authors element
        authorsElement = doc.createElement('authors')
        registerElement.appendChild(authorsElement)
        for author in (args.get('authors') or []):
            authorElement = doc.createElement('author')
            authorsElement.appendChild(authorElement)
            authorElement.setAttribute('name', author.get('name'))
            authorElement.setAttribute('email', author.get('email'))

        # Path element
        pathElement = doc.createElement('path')
        registerElement.appendChild(pathElement)
        pathElement.appendChild(doc.createTextNode(args.get('path')))

        # MD5 element
        md5Element = doc.createElement('md5')
        registerElement.appendChild(md5Element)
        md5Element.appendChild(doc.createTextNode(args.get('md5')))

        # Encoding element
        encodingElement = doc.createElement('encoding')
        registerElement.appendChild(encodingElement)
        encodingElement.appendChild(doc.createTextNode(args.get('encoding')))

        # Licence element
        licElement = doc.createElement('licence')
        registerElement.appendChild(licElement)
        licElement.appendChild(doc.createTextNode(args.get('licence') \
                                                   or ''))

        # Description element
        descElement = doc.createElement('description')
        registerElement.appendChild(descElement)
        descElement.appendChild(doc.createTextNode(args.get('description') \
                                                   or ''))

        return doc
    

def generatePlainDictConfig(**args):
    """Generate configuration and return DOM object"""

    generator = RegisterConfigGenerator()
    doc = generator.generate(**args)

    return doc


def writePlainDictConfig(doc, path):
    """Write XML file"""

    fd = open(path, 'w')
    xml.dom.ext.PrettyPrint(doc, fd)
    fd.close()
    


class RegisterConfigParser:
    """Parse register configuration"""

    def parse(self, xmlData):
        """Parse XML data"""

        doc = xml.dom.minidom.parseString(xmlData)
        name = None
        format = None
        version = None
        authors = []
        path = None
        md5 = None
        encoding = None
        licence = None
        description = None

        registers = doc.getElementsByTagName('plain-dictionary')
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

        for versionElement in registerElement.getElementsByTagName('version'):
            for node in versionElement.childNodes:
                version = node.data.strip()

        for authorElement in registerElement.getElementsByTagName('author'):
            authors.append({'name': authorElement.getAttribute('name'),
                            'email': authorElement.getAttribute('email')})

        for md5Element in registerElement.getElementsByTagName('md5'):
            for node in md5Element.childNodes:
                md5 = node.data

        for encodingElement in \
                registerElement.getElementsByTagName('encoding'):
            for node in encodingElement.childNodes:
                encoding = node.data

        for licenceElement in \
                registerElement.getElementsByTagName('licence'):
            for node in licenceElement.childNodes:
                licence = node.data.strip()

        for descElement in \
                registerElement.getElementsByTagName('description'):
            for node in descElement.childNodes:
                description = (description or '') + node.data.strip()

        result = {}
        result['name'] = name
        result['format'] = format
        result['version'] = version
        result['authors'] = authors
        result['path'] = path
        result['md5'] = md5
        result['encoding'] = encoding
        result['licence'] = licence
        result['description'] = description

        return result


def parsePlainDictConfig(configPath):
    """Parse configuration file and return data dictionary"""

    parser = RegisterConfigParser()
    fd = open(configPath)
    xmlData = fd.read()
    fd.close()
    data = parser.parse(xmlData)

    return data



class IndexFileGenerator:
    """Class for generating register configuration files"""

    def generate(self, index):
        """Generate config XML object"""

        doc = xml.dom.minidom.Document()

        indexElement = doc.createElement("index")
        doc.appendChild(indexElement)

        for data, pos in index.items():
            startElement = doc.createElement("element")
            startElement.setAttribute("literal", data)
            startElement.setAttribute("position", str(pos))
            indexElement.appendChild(startElement)

        return doc
    


def generateIndexFile(index):
    """Generate index data and return DOM object"""

    generator = IndexFileGenerator()
    doc = generator.generate(index)

    return doc


def writeIndexFile(doc, path):
    """Write XML file"""

    fd = open(path, 'wb')
    xml.dom.ext.PrettyPrint(doc, fd)
    fd.close()



class IndexFileParser:
    """Parse register configuration"""

    def parse(self, xmlData):
        """Parse XML data"""

        doc = xml.dom.minidom.parseString(xmlData)
        index = {}

        indexElement = doc.getElementsByTagName('index')[0]

        for element in indexElement.getElementsByTagName('element'):
            index[element.getAttribute("literal")] = long(element.getAttribute("position"))

        return index


def parseIndexFile(indexPath):
    """Parse configuration file and return data dictionary"""

    parser = IndexFileParser()
    fd = open(indexPath, 'rb')
    xmlData = fd.read()
    fd.close()
    index = parser.parse(xmlData)

    return index


class AddOnsParser:
    """Parse add-ons file"""

    class EmptyDictionary(meta.Dictionary):
        """Empty dictionary for representing add-on information"""

        name = None
        version = None
        size = None
        checksum = None
        authors = []
        location = None
        desc = None
        atype = None

        def setType(self, t):

            self.atype = t


        def getType(self):

            return self.atype
        

        def setName(self, name):

            self.name = name


        def getName(self):

            return self.name


        def setVersion(self, version):

            self.version = version


        def getVersion(self):

            return self.version


        def setSize(self, size):

            self.size = size


        def getSize(self):

            return self.size


        def setChecksum(self, checksum):

            self.checksum = checksum


        def getChecksum(self):

            return self.checksum


        def addAuthor(self, author):

            self.authors.append(author)


        def getAuthors(self):

            return self.authors


        def setLocation(self, location):

            self.location = location


        def getLocation(self):

            return self.location


        def setDescription(self, desc):

            self.desc = desc


        def getDescription(self):

            return self.desc
        

    def parse(self, xmlData):
        """Parse XML data and return name->info dictionary object"""

        doc = xml.dom.minidom.parseString(xmlData)

        addons = {}

        for addonElement in doc.getElementsByTagName('add-on'):
            name = None
            version = None
            authors = []
            description = None
            size = None
            url = None
            checksum = None

            addonType = addonElement.getAttribute('type')

            for nameElement in addonElement.getElementsByTagName('name'):
                name = _textData(nameElement)

            for versionElement in addonElement.getElementsByTagName('version'):
                version = _textData(versionElement)

            for authorElement in addonElement.getElementsByTagName('author'):
                authors.append({'name': authorElement.getAttribute('name'),
                                'email': authorElement.getAttribute('email')})
                
            for descElement \
                    in addonElement.getElementsByTagName('description'):
                description = _textData(descElement)

            for urlElement in addonElement.getElementsByTagName('url'):
                url = _textData(urlElement)

            for sizeElement in addonElement.getElementsByTagName('size'):
                size = long(_textData(sizeElement))
                
            for sumElement in addonElement.getElementsByTagName('md5'):
                checksum = _textData(sumElement)


            emptyDict = self.EmptyDictionary()
            emptyDict.setName(name)
            emptyDict.setVersion(version)
            emptyDict.authors = [] # To forget an old reference
            for author in authors:
                emptyDict.addAuthor(author)
            emptyDict.setDescription(description)
            emptyDict.setLocation(url)
            emptyDict.setSize(size)
            emptyDict.setChecksum(checksum)

            addons[name] = emptyDict

        return addons


def parseAddOns(xmlData):
    """Wrap add-ons data parsing"""

    parser = AddOnsParser()
    result = parser.parse(xmlData)
    return result



class MainConfigParser:
    """Parse main configuration"""

    def parse(self, xmlData):
        """Parse XML data"""

        doc = xml.dom.minidom.parseString(xmlData)
        props = {}

        configs = doc.getElementsByTagName('main-config')
        if len(configs) == 0:
            raise "Invalid configuration"

        configElement = configs[0]
        
        for node in configElement.childNodes:
            if not node.nodeType == node.ELEMENT_NODE:
                continue
            
            for cnode in node.childNodes:
                name = node.nodeName
                value = cnode.data.strip()
                props[name] = value

        return props


def parseMainConfig(configPath):
    """Parse configuration file and return data dictionary"""

    parser = MainConfigParser()
    fd = open(configPath)
    xmlData = fd.read()
    fd.close()
    data = parser.parse(xmlData)

    return data



class MainConfigGenerator:
    """Class for generating main configuration file"""

    def generate(self, props):
        """Generate config XML object"""

        doc = xml.dom.minidom.Document()

        mainElement = doc.createElement("main-config")
        doc.appendChild(mainElement)

        for key, value in props.items():
            elem = doc.createElement(key)
            mainElement.appendChild(elem)
            if type(value) != unicode:
                value = str(value)
            elem.appendChild(doc.createTextNode(value))

        return doc
    

def generateMainConfig(props):
    """Generate configuration and return DOM object"""

    generator = MainConfigGenerator()
    doc = generator.generate(props)

    return doc


def writeConfig(doc, path):
    """Write XML file"""

    fd = open(path, 'w')
    xml.dom.ext.PrettyPrint(doc, fd)
    fd.close()

