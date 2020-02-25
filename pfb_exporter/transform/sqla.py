"""
Transform SQLAlchemy Models to Gen3 Data Dictionary
"""
import os
import logging
from pprint import pprint, pformat

from pfb_exporter.transform.base import Transformer


class SqlaTransformer(Transformer):

    def __init__(self, model_dir, output_dir):
        super().__init__(model_dir, output_dir)
        self.logger = logging.getLogger(type(self).__name__)
        self.model_dict = None

    def _import_models(self):
        """
        Import the SQLAlchemy model classes from the Python modules
        in model_dir
        """
        self.logger.debug(f'Importing SQLAlchemy models from {self.model_dir}')

        def _import_model(filepath):
            pass

        if (os.path.isfile(self.model_dir) and
                os.path.splitext(self.model_dir)[-1] == '.py'):
            filepaths = [self.model_dir]
        else:
            filepaths = [
                os.path.join(root, fn)
                for root, dirs, files in os.walk(self.model_dir)
                for fn in files
                if os.path.splitext(fn)[-1] == '.py'
            ]

        self.logger.debug(
            f'Found {len(filepaths)} Python modules:\n{pformat(filepaths)}'
        )

        for fp in filepaths:
            m = _import_model(fp)
            self.model_dict[m.__name__] = m

    def _build_data_dict(self):
        self.logger.info('Build Gen3 data dictionary from SqlAlchemy models')
        self._import_models()
        return {}

    def _model_to_data_dict(self, filepath, data_dict):
        pass
