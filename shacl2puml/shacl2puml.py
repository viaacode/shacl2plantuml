import hashlib

from rdflib import Graph
from rdflib.namespace import RDF, RDFS, SKOS, Namespace

SHACL = Namespace("http://www.w3.org/ns/shacl#")


def shacl_to_puml(args):
    def to_id(term):
        return hashlib.md5(term.encode()).hexdigest()

    def to_local_name(term):
        return term.toPython().rsplit("/", 1)[-1].rsplit("#", 1)[-1]

    def to_label(term):
        if term is None:
            return ""
        if args.nonamespaces is not None:
            return to_local_name(term)
        return term.n3(g.namespace_manager)

    def to_qualifier(min_count, max_count):

        if max_count is None:
            max_count = "*"

        if min_count is None:
            min_count = "0"

        return "[{}..{}]".format(min_count, max_count)

    def print_header():
        print(
            """
@startuml
skinparam classFontSize 14
!define LIGHTORANGE
skinparam componentStyle uml2
skinparam wrapMessageWidth 100
skinparam ArrowColor #Maroon
' Remove shadows
skinparam shadowing false
            """
        )

    def print_namespaces(graph):
        print("legend top right")
        for prefix, uri in graph.namespace_manager.namespaces():
            print("{} = {}".format(prefix, uri))

        print("endlegend")

    def print_class(term):
        print('class "{}" as {}'.format(to_label(term), to_id(term)))

    def print_inheritance(child, parent):
        print("{} --|> {}".format(to_id(child), to_id(parent)))

    def print_property(from_term, to_term, property_term, min, max):
        print(
            "{} --> {} : {} {}".format(
                to_id(from_term),
                to_id(to_term),
                to_label(property_term),
                to_qualifier(min, max),
            )
        )

    def print_attribute(from_term, property_term, data_type, min, max):
        print(
            "{} : <b>{}</b> : {} {}".format(
                to_id(from_term),
                to_label(property_term),
                to_label(data_type),
                to_qualifier(min, max),
            )
        )

    def print_thesaurus(term_class):
        if (None, RDF.type, term_class) in g:
            id = to_id(term_class)
            id_instances = id + "_i"
            print(
                'enum "Thesaurus of {}" as {} #white {{'.format(
                    to_label(term_class), id_instances
                )
            )

            # for row in g.query("""
            #     SELECT ?c ?b ?n
            #     WHERE {
            #         ?c a ?class.
            #         OPTIONAL { ?c skos:broader ?b }
            #         OPTIONAL { ?c skos:narrower ?n }
            #     }
            # """, initBindings={'class': term}):
            #     print(row)

            for term in g.subjects(RDF.type, term_class):
                # TODO: turn this into proper SKOS printing
                if (term, SKOS.topConceptOf, None) in g:
                    print(to_label(term))
                else:
                    broader_term = g.value(term, SKOS.broader)
                    print(
                        "<i>{} -> </i>".format(to_label(broader_term)), to_label(term)
                    )
            print("}")
            print("{} -[hidden]> {}".format(id, id_instances))

    g = Graph()
    for file in args.input:
        g.parse(file, format=args.format)

    print_header()

    if args.nonamespaces is None:
        print_namespaces(g)

    for node_shape in g.subjects(RDF.type, RDFS.Class):
        print_class(node_shape)
        # print all inheritance
        for parent_class in g.objects(node_shape, RDFS.subClassOf):
            print_class(parent_class)
            print_inheritance(node_shape, parent_class)

        # print all properties
        for property_shape in g.objects(node_shape, SHACL.property):

            property_name = g.value(property_shape, SHACL.path)
            data_type = g.value(property_shape, SHACL.datatype)
            class_name = g.value(property_shape, SHACL["class"])
            min_count = g.value(property_shape, SHACL.minCount)
            max_count = g.value(property_shape, SHACL.maxCount)
            node_kind = g.value(property_shape, SHACL.nodeKind)

            if class_name is not None:
                print_class(class_name)
                print_property(
                    node_shape, class_name, property_name, min_count, max_count
                )
            elif data_type is not None:
                print_attribute(
                    node_shape, property_name, data_type, min_count, max_count
                )
            else:
                print_attribute(
                    node_shape, property_name, node_kind, min_count, max_count
                )

        # print possible instances
        # if args.thesauri is not None:
        print_thesaurus(node_shape)

    print(
        """
hide circle
hide methods
hide empty members
@enduml
    """
    )
