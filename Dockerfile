FROM python:3
ADD shacl2puml.py /
RUN pip install rdflib
CMD [ "python", "./shacl2puml.py" ]