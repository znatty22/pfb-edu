"""
Create a PFB (Portable Bioinformatics Format) to compress and serialize data
from a relational database

A PFB file is actually just an Avro file with a particular schema suited to
capture relational data and reconstruct a relational database from it.

PFB creation consists of a few steps:

1. Create a Gen3 data dictionary which represents the relational model that the
data conforms to

2. Add the data dictionary to the PFB file

3. Add the JSON data to the PFB file. The data must conform to the data
dictionary

The first step is accomplished by the PfbExporter's transformer and the
second two steps are executed by the PfbExporter.export method.
"""
import os
import logging
import subprocess
import timeit

from pfb_exporter.config import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PFB_FILE,
    DEFAULT_AVRO_SCHEMA_FILE
)
from pfb_exporter.utils import (
    import_module_from_file,
    import_subclass_from_module,
    setup_logger,
    seconds_to_hms
)
from pfb_exporter.transform.base import Transformer


class PfbExporter(object):

    def __init__(
        self, models_filepath, data_dir, transform_module_filepath,
        output_dir=DEFAULT_OUTPUT_DIR
    ):
        setup_logger(os.path.join(output_dir, 'logs'))
        self.logger = logging.getLogger(type(self).__name__)
        self.models_filepath = os.path.abspath(
            os.path.expanduser(models_filepath)
        )
        self.data_dir = os.path.abspath(os.path.expanduser(data_dir))
        self.output_dir = os.path.abspath(os.path.expanduser(output_dir))
        # Temporary file to write the avro schema to
        self.avro_schema_file = os.path.join(
            output_dir, DEFAULT_AVRO_SCHEMA_FILE
        )
        # Output PFB file
        self.pfb_file = os.path.join(output_dir, DEFAULT_PFB_FILE)
        # Relational model to Gen3 data dict transformer
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
                self.models_filepath, self.output_dir
            )

    def export(self, output_to_pfb=True):
        """
        Create a PFB file containing JSON payloads which conform to a
        relational model

        - Transform the relational model into a Gen3 data dictionary
        - Add data dictionary to PFB file (become PFB schema)
        - Add JSON payloads to PFB file (becomes PFB data)

        :param output_to_pfb: whether to complete the export after transforming
        the relational model to the data dictionary
        :type output_to_pfb: bool
        """
        try:
            # Transform relational model to data dictionary
            self.transformer.transform()
            # Create the PFB file from the data dictionary and data
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
        finally:
            if os.path.isfile(self.avro_schema_file):
                os.remove(self.avro_schema_file)

    def _create_pfb(self):
        """
        Create a PFB file from a Gen3 data dictionary and JSON payloads
        """
        # Add schema to temporary avro file
        self.logger.info(
            f'Add data dict in {self.transformer.data_dict_file} to '
            f'pfb file {self.avro_schema_file}'
        )
        invoke_pfb_cmd(
            self.logger,
            f'from -o {self.avro_schema_file} dict '
            f'{self.transformer.data_dict_file}'
        )
        # Add data to PFB file
        self.logger.info(
            f'Add data in {self.data_dir} to '
            f'pfb file {self.pfb_file}'
        )
        invoke_pfb_cmd(
            self.logger,
            f'from -o {self.pfb_file} json '
            f'-s {self.avro_schema_file} '
            '--program "Kids First" --project "DRC" '
            f'{self.data_dir}'
        )


def invoke_pfb_cmd(logger, cmd_str):
    """
    Invoke PFB CLI with the command and args specified in cmd_str
    """
    cmd_str = f'pfb {cmd_str}'
    logger.debug(f'Invoking PFB with:\n{cmd_str}')

    start_time = timeit.default_timer()
    output = subprocess.run(
        cmd_str, shell=True, stdout=subprocess.PIPE
    )
    total_time = timeit.default_timer() - start_time

    output.check_returncode()

    logger.debug(f'Time elapsed: {seconds_to_hms(total_time)}')
