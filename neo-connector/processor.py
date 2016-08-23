from neo4j.v1 import GraphDatabase, basic_auth
from lxml import etree


def connect_to_neo(url="bolt://0.0.0.0:32768", user='neo4j', password='neo'):
    driver = GraphDatabase.driver(url, auth=basic_auth(user, password))
    return driver.session()


def get_records():
    session = connect_to_neo()
    result = session.run(
        "Match (m:Movie) return id(m) as id, m.title as title, m.tagline as tagline, m.released as released")

    for record in result:
        yield {'id': record['id'], 'title': record['title'],
               'description': record['tagline'],
               'released': record['released']}


def get_xml(record_id, creator, publisher, language, rights, title,
            description, date):
    namespace = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'
    root = etree.Element(namespace + 'record')

    lan = etree.SubElement(root, namespace + 'language')
    lan.text = language

    t = etree.SubElement(root, namespace + 'title')
    t.text = title

    d = etree.SubElement(root, namespace + 'description')
    d.text = description

    r = etree.SubElement(root, namespace + 'rights')
    r.text = rights

    etree.SubElement(root, namespace + 'date', created=str(date))

    ident = etree.SubElement(root, namespace + 'identifier')
    ident.text = str(record_id)

    cr = etree.SubElement(root, namespace + 'creator')
    cr.text = creator

    pub = etree.SubElement(root, namespace + 'publisher')
    pub.text = publisher

    return root


if __name__ == "__main__":
    output_directory = '/tmp/'
    file_name_prefix = 'movie'

    print('Storing data in %s' % output_directory)
    for r in get_records():
        xml = get_xml(record_id=r['id'], creator='jj', publisher='EUDAT',
                      language='en', rights='open', title=r['title'],
                      description=r['description'], date=r['released'])

        with open('%s/%s-%s.xml' % (output_directory, file_name_prefix,
                                    r['id']), 'w+') as fg:
            fg.write(etree.tostring(xml, pretty_print=True))
