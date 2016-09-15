from neo4j.v1 import GraphDatabase, basic_auth, exceptions
import os


def connect_to_neo(url="bolt://0.0.0.0:32768", user='neo4j', password='neo'):
    try:
        driver = GraphDatabase.driver(url, auth=basic_auth(user, password))
        return driver.session()
    except exceptions.ProtocolError:
        print('Unable to connect to neo4j at %s' % url)
        exit(-1)


def get_records(session):
    """ get some data from neo4j,

    this is just an example that works with neo4j default movies database
    """
    result = session.run(
        "Match (m:Movie) return id(m) as id, m.title as title, "
        "m.tagline as tagline, m.released as released")

    for record in result:
        yield {
            'identifier': record['id'],
            'title': record['title'],
            'description': record['tagline'],
            'created': record['released']
        }


def get_xml(record_id, creator, publisher, language, rights, title,
            description, date):
    """ transforms data into somethig close to DC Xml representation
     this method is much more sophisiticated and secure
    """
    from lxml import etree
    namespace = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
    root = etree.Element(namespace + 'record')

    lan = etree.SubElement(root, namespace + 'language')
    lan.text = language

    t = etree.SubElement(root, namespace + 'title')
    t.text = title

    d = etree.SubElement(root, namespace + 'description')
    d.text = description

    rwr = etree.SubElement(root, namespace + 'rights')
    rwr.text = rights

    etree.SubElement(root, namespace + 'date', created=str(date))

    ident = etree.SubElement(root, namespace + 'identifier')
    ident.text = str(record_id)

    cr = etree.SubElement(root, namespace + 'creator')
    cr.text = creator

    pub = etree.SubElement(root, namespace + 'publisher')
    pub.text = publisher

    return root


def get_xml_alt(content):
    from string import Template
    t = Template(
        "<ns0:record xmlns:ns0=\"http://www.openarchives.org/OAI/2.0/oai_dc"
        "/\">\n"
        "<ns0:language>$language</ns0:language>\n"
        "<ns0:title>$title</ns0:title>\n"
        "<ns0:description>$description</ns0:description>\n"
        "<ns0:rights>$rights</ns0:rights>\n"
        "<ns0:date created=\"$created\"/>\n"
        "<ns0:identifier>$identifier</ns0:identifier>\n"
        "<ns0:creator>$creator</ns0:creator>\n"
        "<ns0:publisher>$publisher</ns0:publisher>\n"
        "</ns0:record>")
    defaults = dict(
        language='en',
        rights='open',
        date='2016',
        publisher='EUDAT',
        creator='EUDAT'
    )

    # t.safe_substitute(z)
    # it should generate an exception if a field is not set despite some
    # defaults
    defaults.update(content)
    return t.substitute(defaults)


if __name__ == "__main__":
    uri = os.getenv('NEO4J_URI', 'bolt://0.0.0.0:7687')
    u = os.getenv('NEO4J_USER', 'neo4j')
    p = os.getenv('NEO4j_PASS', 'neo')
    print('Connecting to neo4j at %s as (%s)' % (uri, u))

    s = connect_to_neo(uri, u, p)

    output_directory = os.getenv('OUTPUT_DIR', '/tmp/')
    file_name_prefix = os.getenv('OUTPUT_PREFIX', 'movie')

    print('Storing data in %s' % output_directory)
    for r in get_records(session=s):
        # xml = get_xml(record_id=r['identifier'], creator='jj',
        # publisher='EUDAT',
        #               language='en', rights='open', title=r['title'],
                      # description=r['description'], date=r['created'])
        xml = get_xml_alt(r)

        with open('%s/%s-%s.xml' % (output_directory, file_name_prefix,
                                    r['identifier']), 'w+') as fg:
            fg.write(xml.encode('UTF-8'))
