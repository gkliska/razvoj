from xmlparser cimport xmlSAXHandler
from tree cimport xmlDoc

cdef extern from "libxml/xmlschemas.h":
    ctypedef struct xmlSchema
    ctypedef struct xmlSchemaParserCtxt

    ctypedef struct xmlSchemaSAXPlugStruct
    ctypedef struct xmlSchemaValidCtxt

    cdef xmlSchemaValidCtxt* xmlSchemaNewValidCtxt(xmlSchema* schema) nogil
    cdef int xmlSchemaValidateDoc(xmlSchemaValidCtxt* ctxt, xmlDoc* doc) nogil
    cdef xmlSchema* xmlSchemaParse(xmlSchemaParserCtxt* ctxt) nogil
    cdef xmlSchemaParserCtxt* xmlSchemaNewParserCtxt(char* URL) nogil
    cdef xmlSchemaParserCtxt* xmlSchemaNewDocParserCtxt(xmlDoc* doc) nogil
    cdef void xmlSchemaFree(xmlSchema* schema) nogil
    cdef void xmlSchemaFreeParserCtxt(xmlSchemaParserCtxt* ctxt) nogil
    cdef void xmlSchemaFreeValidCtxt(xmlSchemaValidCtxt* ctxt) nogil

    cdef xmlSchemaSAXPlugStruct* xmlSchemaSAXPlug(xmlSchemaValidCtxt* ctxt,
                                                  xmlSAXHandler** sax,
                                                  void** data) nogil
    cdef int xmlSchemaSAXUnplug(xmlSchemaSAXPlugStruct* sax_plug)
    cdef int xmlSchemaIsValid(xmlSchemaValidCtxt* ctxt)
