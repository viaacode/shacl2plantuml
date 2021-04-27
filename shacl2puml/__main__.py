
#!/usr/bin/env python
# coding: utf-8

from .shacl2puml import shacl_to_puml

import argparse

def main():
    parser = argparse.ArgumentParser(description="Generates Plant UML diagrams from the Shapes Constraint Language (SHACL).")
    parser.add_argument('input', metavar='shaclFile.ttl', nargs='+',
                    help='The SHACL file to generate the Plant UML diagram for.')
    parser.add_argument('-f', '--format', default='ttl',
                    help='The RDF serialization of the SHACL file.')
    parser.add_argument('-n', '--no-namespaces', dest='nonamespaces', 
                    help='Do not use prefixes when printing labels.')
    # parser.add_argument('-t', '--thesauri',
    #                 help='Print SKOS instances.')
    args = parser.parse_args()

    shacl_to_puml(args)

if __name__ == "__main__":
    main()