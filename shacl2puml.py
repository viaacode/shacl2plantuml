#!/usr/bin/env python
# coding: utf-8

from rdflib import Graph
from rdflib.namespace import Namespace
from rdflib.namespace import RDF, RDFS
import hashlib
import argparse

SHACL = Namespace("http://www.w3.org/ns/shacl#")

NODEKINDS = {
    SHACL.IRI: "IRI",
    SHACL.BlankNode: "",
    SHACL.BlankNodeOrIRI: "",
    SHACL.IRIOrLiteral: "",
    SHACL.BlankNodeOrLiteral: "",
    SHACL.IRIOrLiteral:""
}

def main(args):

    print("""
@startuml
skinparam classFontSize 14
!define LIGHTORANGE
skinparam componentStyle uml2
skinparam wrapMessageWidth 100
skinparam ArrowColor #Maroon
    """)

    g = Graph()
    for file in args.input:
        g.parse(file, format=args.format)

    def to_id(term):
        return hashlib.md5(term.encode()).hexdigest()

    def to_local_name(term):
        return term.toPython().rsplit('/', 1)[-1].rsplit('#', 1)[-1]

    def to_label(term):
        if term is None:
            return ""
        if 'nonamespaces' in args:
            return to_local_name(term)
        return term.n3(g.namespace_manager)

    def to_qualifier(min, max):
        
        if max is None:
            max = '*'
        
        if min is None:
            min = '0'
        
        return "[{}..{}]".format(min, max)

    def print_namespaces(graph):
        print("legend top left")
        for prefix, uri in graph.namespace_manager.namespaces():
            print("{} = {}".format(prefix, uri))

        print("endlegend")

    def print_class(term):
        print("class \"{}\" as {}".format(to_label(term), to_id(term)))
    
    def print_property(from_term, to_term, property, min, max):
        print("{} --> {} : {} {}".format(to_id(from_term), to_id(to_term), to_label(property), to_qualifier(min, max)))

    def print_attribute(from_term, property, dataType, min, max):
        print("{} : <b>{}</b> : {} {}".format(to_id(from_term), to_label(property), to_label(dataType), to_qualifier(min, max)))

    if 'nonamespaces' not in args:
        print_namespaces(g)

    for nodeShape in g.subjects(RDF.type, RDFS.Class):
        print_class(nodeShape)
        
        for parentClass in g.objects(nodeShape,  RDFS.subClassOf):
            print_class(parentClass)
            print("{} --|> {}".format(to_id(nodeShape), to_id(parentClass)))
        
        for propertyShape in g.objects(nodeShape,  SHACL.property):
            
            propertyName = g.value(propertyShape, SHACL.path)
            dataType = g.value(propertyShape, SHACL.datatype)
            className = g.value(propertyShape, SHACL['class'])
            minCount = g.value(propertyShape, SHACL.minCount)
            maxCount = g.value(propertyShape, SHACL.maxCount)
            nodeKind = g.value(propertyShape, SHACL.nodeKind)
            
            if className is not None:
                print_class(className)
                print_property(nodeShape, className, propertyName, minCount, maxCount)
            elif dataType is not None:
                print_attribute(nodeShape, propertyName, dataType, minCount, maxCount)
            else:
                print_attribute(nodeShape, propertyName, nodeKind, minCount, maxCount)

    print("""
hide circle
hide methods
hide empty members
@enduml
    """)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates Plant UML diagrams from the Shapes Constraint Language (SHACL).")
    parser.add_argument('input', metavar='shaclFile.ttl', nargs='+',
                    help='The SHACL file to generate the Plant UML diagram for.')
    parser.add_argument('-f', '--format', default='ttl',
                    help='The RDF serialization of the SHACL file.')
    parser.add_argument('-n', '--no-namespaces', dest='nonamespaces', action='store_true',
                    help='Do not use prefixes when printing labels.')
    args = parser.parse_args()

    main(args)