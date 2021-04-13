#!/usr/bin/env python
# coding: utf-8

from rdflib import Graph
from rdflib.namespace import Namespace
from rdflib.namespace import RDF, RDFS, SKOS
import hashlib
import argparse

SHACL = Namespace("http://www.w3.org/ns/shacl#")

def to_id(term):
    return hashlib.md5(term.encode()).hexdigest()

def to_local_name(term):
    return term.toPython().rsplit('/', 1)[-1].rsplit('#', 1)[-1]

def to_label(term, namespace_manager= None):
    if term is None:
        return ""
    if namespace_manager is None:
        return to_local_name(term)
    return term.n3(namespace_manager)

def to_qualifier(min, max):

    if max is None:
        max = '*'

    if min is None:
        min = '0'

    return "[{}..{}]".format(min, max)

def main(args):

    print("""
@startuml
skinparam classFontSize 14
!define LIGHTORANGE
skinparam componentStyle uml2
skinparam wrapMessageWidth 100
skinparam ArrowColor #Maroon
' Remove shadows
skinparam shadowing false
    """)

    g = Graph()
    for file in args.input:
        g.parse(file, format=args.format)

    def print_namespaces():
        print("legend top left")
        for prefix, uri in g.namespace_manager.namespaces():
            print("{} = {}".format(prefix, uri))

        print("endlegend")

    def print_class(term):
        term_label = (args.nonamespaces and to_label(term)) or to_label(term, g.namespace_manager)
        print("class \"{}\" as {}".format(term_label, to_id(term)))

    def print_inheritance(child, parent):
        print("{} --|> {}".format(to_id(child), to_id(parent)))

    def print_property(from_term, to_term, property, min, max):
        property_label = (args.nonamespaces and to_label(property)) or to_label(property, g.namespace_manager)
        print("{} --> {} : {} {}".format(to_id(from_term),
              to_id(to_term), property_label, to_qualifier(min, max)))

    def print_attribute(from_term, property, datatype, min, max):
        property_label = (args.nonamespaces and to_label(property)) or to_label(property, g.namespace_manager)
        datatype_label = (args.nonamespaces and to_label(datatype)) or to_label(datatype, g.namespace_manager)
        print("{} : <b>{}</b> : {} {}".format(to_id(from_term),
              property_label, datatype_label, to_qualifier(min, max)))

    def print_thesaurus(term_class):
        if (None, RDF.type,  term_class) in g:
            id = to_id(term_class)
            id_instances = id + "_i"
            term_class_label = (args.nonamespaces and to_label(term_class)) or to_label(term_class, g.namespace_manager)

            print("enum \"Thesaurus of {}\" as {} #white {{".format(
                term_class_label, id_instances))

            # for row in g.query("""
            #     SELECT ?c ?b ?n
            #     WHERE {
            #         ?c a ?class.
            #         OPTIONAL { ?c skos:broader ?b }
            #         OPTIONAL { ?c skos:narrower ?n }
            #     }
            # """, initBindings={'class': term}):
            #     print(row)

            for term in g.subjects(RDF.type,  term_class):
                # TODO: turn this into proper SKOS printing
                term_label = (args.nonamespaces and to_label(term)) or to_label(term, g.namespace_manager)
                if (term, SKOS.topConceptOf, None) in g:
                    print(term_label)
                else:
                    broader_term = g.value(term, SKOS.broader)
                    broader_term_label = (args.nonamespaces and to_label(broader_term)) or to_label(broader_term, g.namespace_manager)
                    print('<i>{} -> </i>'.format(broader_term_label), term_label)
            print("}")
            print("{} -[hidden]> {}".format(id, id_instances))

    if not args.nonamespaces:
        print_namespaces()

    for nodeShape in g.subjects(RDF.type, RDFS.Class):
        print_class(nodeShape)
        # print all inheritance
        for parentClass in g.objects(nodeShape,  RDFS.subClassOf):
            print_class(parentClass)
            print_inheritance(nodeShape, parentClass)

        # print all properties
        for propertyShape in g.objects(nodeShape,  SHACL.property):

            propertyName = g.value(propertyShape, SHACL.path)
            dataType = g.value(propertyShape, SHACL.datatype)
            className = g.value(propertyShape, SHACL['class'])
            minCount = g.value(propertyShape, SHACL.minCount)
            maxCount = g.value(propertyShape, SHACL.maxCount)
            nodeKind = g.value(propertyShape, SHACL.nodeKind)

            if className is not None:
                print_class(className)
                print_property(nodeShape, className,
                               propertyName, minCount, maxCount)
            elif dataType is not None:
                print_attribute(nodeShape, propertyName,
                                dataType, minCount, maxCount)
            else:
                print_attribute(nodeShape, propertyName,
                                nodeKind, minCount, maxCount)

        # print possible instances
        # if args.thesauri is not None:
        print_thesaurus(nodeShape)

    print("""
hide circle
hide methods
hide empty members
@enduml
    """)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates Plant UML diagrams from the Shapes Constraint Language (SHACL).")
    parser.add_argument('input', metavar='shaclFile.ttl', nargs='+',
                        help='The SHACL file to generate the Plant UML diagram for.')
    parser.add_argument('-f', '--format', default='ttl',
                        help='The RDF serialization of the SHACL file.')
    parser.add_argument('-n', '--no-namespaces', dest='nonamespaces', action='store_true',
                        help='Do not use prefixes when printing labels.')
    # parser.add_argument('-d', '--docs', default='README.md', type=argparse.FileType('w'),
    #                     help='Also output simple docs in markdown.')
    # parser.add_argument('-t', '--thesauri',
    #                 help='Print SKOS instances.')
    args = parser.parse_args()

    main(args)
