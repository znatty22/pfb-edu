from abc import ABC, abstractmethod
import os
import json
import logging

from pfb_exporter.config import DEFAULT_DATA_DICT_FILE


class Transformer(ABC):

    def __init__(self, model_dir, output_dir):
        self.logger = logging.getLogger(type(self).__name__)
        self.model_dir = model_dir
        self.output_dir = output_dir

    @abstractmethod
    def _build_data_dict(self, *args, **kwargs):
        """
        Must be implemented by child classes and output a dict representing
        the entities in the Gen3 data dictionary.
        """
        return {}

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
        dd = self._build_data_dict(*args, **kwargs)
        self.write_data_dict(dd)
        self.logger.info(
            'END transformation from relational model to Gen3 '
            'data dictionary'
        )

    def write_data_dict(self, data):
        """
        Write the Gen3 data dictionary created by self.transform to the
        output_dir as a set of yaml files. There will be one YAML file per
        entity

        :param data: data needed to write out the Gen3 data dict files
        :type data: dict
        :returns: path to directory containing data dict files
        """
        self.data_dict_file = os.path.join(
            self.output_dir, DEFAULT_DATA_DICT_FILE
        )
        if data:
            self.logger.info(
                f'Writing data dictionary files to {self.data_dict_file}'
            )
            with open(self.data_dict_file, 'w') as json_file:
                json.dump(data, json_file, indent=4, sort_keys=True)
