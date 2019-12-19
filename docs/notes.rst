Notes
=====

Look for this in the XML::

    <?xml version="1.0" encoding="UTF-8"?>
    <?xml-model href="http://pds.nasa.gov/pds4/schema/released/pds/v1/PDS4_PDS_1101.sch" ?>
    <Product_Bundle xmlns="http://pds.nasa.gov/pds4/pds/v1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/schema/released/pds/v1/PDS4_PDS_1101.xsd">
        …
        <Bundle_Member_Entry>
            <lid_reference>urn:nasa:pds:ladee_mission:xml_schema_collection</lid_reference>
            <member_status>Primary</member_status>
            <reference_type>bundle_has_schema_collection</reference_type>
        </Bundle_Member_Entry>
        <Bundle_Member_Entry>
            <lid_reference>urn:nasa:pds:ladee_mission:document_collection</lid_reference>
            <member_status>Primary</member_status>
            <reference_type>bundle_has_document_collection</reference_type>
        </Bundle_Member_Entry>
        <Bundle_Member_Entry>
            <lid_reference>urn:nasa:pds:ladee_mission:context_collection</lid_reference>
            <member_status>Primary</member_status>
            <reference_type>bundle_has_context_collection</reference_type>
        </Bundle_Member_Entry>
    </Product_Bundle>

When the ``member_status`` is ``Primary``, then look up each ``lid_reference`` in Solr::

    import pysolr
    s = pysolr.Solr('https://pds-dev-el7.jpl.nasa.gov/services/registry/pds', verify=False)
    results = s.search('lid:"urn:nasa:pds:ladee_mission:xml_schema_collection"')

Iterate through ``results`` and look for ``file_ref_url``. 


Grabbing Data
-------------

Try::

    wget -erobots=off --cut-dirs=1 --reject='index.html*' --no-host-directories --mirror --no-parent --relative --timestamping --no-check-certificate --recursive https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/mission_bundle/

.. Copyright © 2019 California Institute of Technology ("Caltech").
   ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
