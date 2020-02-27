"""
Export biomedical data from a relational database to an Avro file.

An Avro file stores the data schema as a JSON blob and the data in a
binary format

See https://avro.apache.org for details

In this case, the Avro file is called a PFB
(Portable Format for Bioinformatics) file because the data in the Avro file
conforms to the PFB schema, which is a graph structure suitable for capturing
relational data.

PFB file creations involves the following steps:

1. Create a PFB schema to represent the relational database
2. Transform the data from the relational database into the graph form
3. Add the PFB schema to the Avro file as an Avro schema
4. Add the transformed graph data to the Avro file as data records

Supported Databases:
- Any of the databases supported by SQLAlchemy since the SQLAlchemy ORM
is used to inspect the database and autogenerate the SQLAlchemy models
which are in turn used to create the PFB Schema.
"""
import os
import logging

from pfb_exporter.config import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PFB_FILE,
    DEFAULT_MODELS_PATH,
    DEFAULT_TRANFORM_MOD
)
from pfb_exporter.utils import (
    import_module_from_file,
    import_subclass_from_module,
    setup_logger
)
from pfb_exporter.transform.base import Transformer


class PfbExporter(object):

    def __init__(
        self,
        data_dir,
        db_conn_url=None,
        models_filepath=DEFAULT_MODELS_PATH,
        transform_module_filepath=DEFAULT_TRANFORM_MOD,
        output_dir=DEFAULT_OUTPUT_DIR
    ):
        setup_logger(os.path.join(output_dir, 'logs'))
        self.logger = logging.getLogger(type(self).__name__)
        self.models_filepath = os.path.abspath(
            os.path.expanduser(models_filepath)
        )
        self.data_dir = os.path.abspath(os.path.expanduser(data_dir))
        self.output_dir = os.path.abspath(os.path.expanduser(output_dir))

        self.pfb_file = os.path.join(output_dir, DEFAULT_PFB_FILE)

        # Relational model to PFB Schema transformer
        self.transformer = None

        # Import transformer subclass class from transform module
        mod = import_module_from_file(transform_module_filepath)
        child_classes = import_subclass_from_module(Transformer, mod)

        if not child_classes:
            raise NotImplementedError(
                f'Transform module {transform_module_filepath} must implement '
                f'a class which extends the abstract base class '
                f'{os.path.abspath(mod.__file__)}. + {Transformer.__name__}'
            )
        else:
            self.transformer = child_classes[0](
                self.models_filepath, self.output_dir, db_conn_url=db_conn_url
            )

    def export(self, output_to_pfb=True):
        """
        Create a PFB file containing JSON payloads which conform to a
        relational model

        - Transform the relational model into a PFB Schema
        - Transform the data into PFB Entities
        - Create an Avro file with the PFB schema and Entities

        :param output_to_pfb: whether to complete the export after transforming
        the relational model to the PFB schema
        :type output_to_pfb: bool
        """
        try:
            # Transform relational model to PFB Schema
            self.transformer.transform()
            # Create the PFB file from the PFB Schema and data
            if output_to_pfb:
                self._create_pfb()
        except Exception as e:
            self.logger.exception(str(e))
            self.logger.info(f'❌ Export to PFB file {self.pfb_file} failed!')
            exit(1)
        else:
            self.logger.info(
                f'✅ Export to PFB file {self.pfb_file} succeeded!'
            )

    def _create_pfb(self):
        """
        Create a PFB file from a Gen3 PFB Schema and JSON payloads
        """
        # Add schema to temporary avro file
        pass
