#!/usr/bin/env python
# coding: utf-8

from rdflib import Graph
from rdflib.namespace import Namespace
from rdflib.namespace import RDF, RDFS
import hashlib
import argparse

SHACL = Namespace("http://www.w3.org/ns/shacl#")

def main(args):

    print("""
@startuml
skinparam classFontSize 14
!define LIGHTORANGE
skinparam componentStyle uml2
skinparam wrapMessageWidth 100
skinparam ArrowColor #Maroon
skinparam linetype ortho
    """)

    g = Graph()
    g.parse(args.input, format=args.format)

    def to_id(term):
        return hashlib.md5(term.encode()).hexdigest()

    def to_label(term):
        if term is None:
            return ""
        return term.n3(g.namespace_manager)

    def to_qualifier(min, max):
        
        if max is None:
            max = '*'
        
        if min is None:
            min = '0'
        
        return "[{}..{}]".format(min, max)

    def print_class(term):
        print("class \"{}\" as {}".format(to_label(term), to_id(term)))

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
            
            if className is not None:
                print_class(className)
                print("{} --> {} : {} {}".format(to_id(nodeShape), to_id(className), to_label(propertyName), to_qualifier(minCount, maxCount)))
            else:
                print("{} : <b>{}</b> : {} {}".format(to_id(nodeShape), to_label(propertyName), to_label(dataType), to_qualifier(minCount, maxCount)))

    print("""
hide circle
hide methods
hide empty members
@enduml
    """)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates Plant UML diagrams from the Shapes Constraint Language (SHACL).")
    parser.add_argument('input', metavar='shaclFile.ttl',
                    help='The SHACL file to generate the Plant UML diagram for.')
    parser.add_argument('-f', '--format', default='ttl',
                    help='The RDF serialization of the SHACL file.')
    args = parser.parse_args()

    main(args)