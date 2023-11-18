#!/usr/bin/env python

import sys
import os
import zipfile
import md5
import xml.dom.minidom

#
# Add-ons description file generator for OpenDict
# Copyright (c) 2005 Martynas Jocius <martynas.jocius@idiles.com>
#
# Fast code, dirty code
#

def parsePluginConfig(xmlData):
    """Parse plugin configuration"""

    doc = xml.dom.minidom.parseString(xmlData)

    name = None
    version = None
    authors = []
    description = None
    
    pluginElement = doc.getElementsByTagName('plugin')[0]
    pluginType = pluginElement.getAttribute('type')

    if pluginType != 'dictionary':
        raise Exception("Plugin is not dictionary plugin")

    # Get name
    for nameElement in doc.getElementsByTagName('name'):
        for node in nameElement.childNodes:
            if node.nodeType == node.TEXT_NODE:
                name = node.data

    # Get version
    for versionElement in doc.getElementsByTagName('version'):
        for node in versionElement.childNodes:
            if node.nodeType == node.TEXT_NODE:
                version = node.data

    # Get authors
    for authorElement in doc.getElementsByTagName('author'):
        authorName = authorElement.getAttribute('name')
        authorEMail = authorElement.getAttribute('email')
        authors.append({'name': authorName, 'email': authorEMail})

    # Get description
    for descElement in doc.getElementsByTagName('description'):
        for node in descElement.childNodes:
            if node.nodeType == node.TEXT_NODE:
                description = node.data


    
    result = {}
    result['name'] = name
    result['version'] = version
    result['authors'] = authors
    result['description'] = description

    return result


def parsePlainConfig(xmlData):
    """Parse plain dict configuration"""

    doc = xml.dom.minidom.parseString(xmlData)
    name = None
    version = None
    authors = []
    description = None

    registers = doc.getElementsByTagName('plain-dictionary')
    if len(registers) == 0:
        raise "Invalid configuration"

    registerElement = registers[0]

    for nameElement in registerElement.getElementsByTagName('name'):
        for node in nameElement.childNodes:
            name = node.data

    for versionElement in registerElement.getElementsByTagName('version'):
        for node in versionElement.childNodes:
            version = node.data.strip()

    for authorElement in registerElement.getElementsByTagName('author'):
        authors.append({'name': authorElement.getAttribute('name'),
                        'email': authorElement.getAttribute('email')})

    for descElement in \
            registerElement.getElementsByTagName('description'):
        for node in descElement.childNodes:
            description = (description or '') + node.data.strip()

    result = {}
    result['name'] = name
    result['version'] = version
    result['authors'] = authors
    result['description'] = description

    return result


def generateElement(**args):
    """Generate add-on XML DOM elemente"""
    
    doc = xml.dom.minidom.Document()

    addonElement = doc.createElement('add-on')
    addonElement.setAttribute('type', args.get('type'))

    # Name element
    nameElement = doc.createElement('name')
    addonElement.appendChild(nameElement)
    nameElement.appendChild(doc.createTextNode(args.get('name')))

    # Version element
    versionElement = doc.createElement('version')
    addonElement.appendChild(versionElement)
    versionElement.appendChild(doc.createTextNode(args.get('version')))

    # Authors element
    authorsElement = doc.createElement('authors')
    addonElement.appendChild(authorsElement)
    for author in (args.get('authors') or []):
        authorElement = doc.createElement('author')
        authorsElement.appendChild(authorElement)
        authorElement.setAttribute('name', author.get('name'))
        authorElement.setAttribute('email', author.get('email'))

    # Description element
    descElement = doc.createElement('description')
    addonElement.appendChild(descElement)
    descEscaped = "%s" % args.get('description', '')
    descElement.appendChild(doc.createTextNode(descEscaped))

    # MD5 element
    md5Element = doc.createElement('md5')
    addonElement.appendChild(md5Element)
    md5Element.appendChild(doc.createTextNode(args.get('md5sum')))

    # URL element
    urlElement = doc.createElement('url')
    addonElement.appendChild(urlElement)
    urlElement.appendChild(doc.createTextNode(args.get('url')))

    # Size element
    sizeElement = doc.createElement('size')
    addonElement.appendChild(sizeElement)
    sizeElement.appendChild(doc.createTextNode(str(args.get('size'))))

    return addonElement


def listFiles(start, followLinks, myDepth, maxDepth):
    """Return file list"""
    
    files = []
    
    try:
        dirList = os.listdir(start)
    except:
        if os.path.isdir(start):
            print('ERROR: Cannot list directory %s' % start)
        return files
    
    for item in dirList:
        path = os.path.join(start, item)
        
        if os.path.isdir(path) and (followLinks or \
                             (not followLinks and not islink(path))):
            files.extend(listFiles(path, followLinks,
                                  myDepth + 1,
                                  maxDepth))
        else:
            files.append(path)

    return files


def makeDocument(addons):
    """Connect add-on elements to one XML document"""

    doc = xml.dom.minidom.Document()
    addonsElement = doc.createElement('opendict-add-ons')
    doc.appendChild(addonsElement)

    for addon in addons:
        addonsElement.appendChild(addon)

    return doc    


def main():
    """Main procedure"""
    
    if len(sys.argv) < 3:
        print("Usage: %s <directory> <base URL>" % sys.argv[0])
        print("(Example: '%s . http://xxx.yyy.net/dicts')" % sys.argv[0])
        sys.exit(1)

    d = sys.argv[1]
    baseURL = sys.argv[2]
    xmlElements = []

    for filePath in listFiles(d, True, 0, None):

        try:
            zipFile = zipfile.ZipFile(filePath, 'r')
        except Exception as e:
            print("ERROR: %s: %s" % (filePath, e))
            continue
        
        # Test CRC
        if zipFile.testzip():
            raise Exception(_("Dictionary plugin file is corrupted"))
        
        # Check if empty
        try:
            topDirectory = zipFile.namelist()[0]
        except Exception as e:
            raise Exception(_("Plugin file is empty (%s)" % e))
        
        # Check for validity
        for fileInZip in zipFile.namelist():
            dirName = os.path.dirname(fileInZip)
            fileName = os.path.basename(fileInZip)

        topDir = zipFile.namelist()[0]

        plainConfigPath = os.path.join(topDir, 'conf', 'config.xml')
        pluginConfigPath = os.path.join(topDir, 'plugin.xml')

        info = {}

        if plainConfigPath in zipFile.namelist():
            info.update(parsePlainConfig(zipFile.read(plainConfigPath)))
            info['type'] = 'plain-dictionary'
        elif pluginConfigPath in zipFile.namelist():
            info.update(parsePluginConfig(zipFile.read(pluginConfigPath)))
            info['type'] = 'plugin-dictionary'

        sz = os.stat(filePath)[6] / 1000

        fd = open(filePath)
        m = md5.new(fd.read())
        fd.close()
        checksum = m.hexdigest()

        location = baseURL + '/' + filePath

        xmlElements.append(generateElement(type=info.get('type'),
                                           name=info.get('name'),
                                           version=info.get('version'),
                                           authors=info.get('authors'),
                                           description=info.get('description'),
                                           url=location,
                                           md5sum=checksum,
                                           size=sz))

        print("* %s" % filePath)

    doc = makeDocument(xmlElements)
    fd = open('opendict-add-ons.xml', 'w')
    fd.write(doc.toxml())
    fd.close()
    

if __name__ == "__main__":
    main()
    
