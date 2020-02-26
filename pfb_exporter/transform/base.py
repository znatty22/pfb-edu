"""
Base class for all Transform SQLAlchemy Models to PFB Schema
"""

from abc import ABC, abstractmethod
import os
import json
import logging

from pfb_exporter.config import DEFAULT_PFB_SCHEMA_FILE


class Transformer(ABC):

    def __init__(self, models_filepath, output_dir):
        self.logger = logging.getLogger(type(self).__name__)
        self.models_filepath = models_filepath
        self.output_dir = output_dir

    @abstractmethod
    def _transform(self, *args, **kwargs):
        raise NotImplementedError()

    def transform(self, *args, **kwargs):
        """
        Transform a relational model into a Gen3 data dictionary and
        write the data dictionary to file

        Positional and keyword args get forwarded to child class's
        _build_data_dict method
        """
        self.logger.info(
            'BEGIN transformation from relational model to Gen3 '
            'data dictionary'
        )
        pfb_schema = self._transform(*args, **kwargs)
        self.write_pfb_schema(pfb_schema)
        self.logger.info(
            'END transformation from relational model to Gen3 '
            'data dictionary'
        )

    def write_pfb_schema(self, data):
        """
        Write the Gen3 data dictionary created by self.transform to the
        output_dir as a set of yaml files. There will be one YAML file per
        entity

        :param data: data needed to write out the Gen3 data dict files
        :type data: dict
        :returns: path to directory containing data dict files
        """
        self.pfb_schema = os.path.join(
            self.output_dir, DEFAULT_PFB_SCHEMA_FILE
        )
        if data:
            self.logger.info(
                f'Writing PFB schema to {self.pfb_schema}'
            )
            with open(self.pfb_schema, 'w') as json_file:
                json.dump(data, json_file, indent=4, sort_keys=True)
