"""
Transform SQLAlchemy Models to Gen3 Data Dictionary
"""
import os
import logging
import inspect
from pprint import pprint, pformat

from sqlalchemy.inspection import inspect as sqla_inspect
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.ext.declarative.api import DeclarativeMeta

from pfb_exporter.utils import import_module_from_file
from pfb_exporter.transform.base import Transformer


class SqlaTransformer(Transformer):

    def __init__(self, models_filepath, output_dir):
        super().__init__(models_filepath, output_dir)
        self.logger = logging.getLogger(type(self).__name__)
        self.data_dict = {}
        self.model_dict = {}

    def _import_models(self):
        """
        Import the SQLAlchemy model classes from the Python modules
        in models_filepath
        """
        self.logger.debug(
            f'Importing SQLAlchemy models from {self.models_filepath}'
        )

        def _import_model_classes_from_file(filepath):
            """
            Import the SQLAlchemy models from the Python module at `filepath`
            """
            imported_model_classes = []
            mod = import_module_from_file(filepath)
            # NOTE - We cannot use
            # pfb_exporter.utils.import_subclass_from_module here because
            # we are unable to use issubclass to test if the SQLAlchemy model
            # class is a subclass of its parent
            # (sqlalchemy.ext.declarative.api.Base)
            # The best we can do is make sure the class is a SQLAlchemy object
            # and check that the object is a DeclarativeMeta type
            for cls_name, cls_path in inspect.getmembers(mod, inspect.isclass):
                cls = getattr(mod, cls_name)
                try:
                    sqla_inspect(cls)
                except NoInspectionAvailable:
                    # Not a SQLAlchemy object
                    pass
                else:
                    if type(cls) == DeclarativeMeta:
                        imported_model_classes.append(cls)

            return imported_model_classes

        if (os.path.isfile(self.models_filepath) and
                os.path.splitext(self.models_filepath)[-1] == '.py'):
            filepaths = [self.models_filepath]
        else:
            filepaths = [
                os.path.join(root, fn)
                for root, dirs, files in os.walk(self.models_filepath)
                for fn in files
                if os.path.splitext(fn)[-1] == '.py'
            ]

        self.logger.debug(
            f'Found {len(filepaths)} Python modules:\n{pformat(filepaths)}'
        )
        # Add the imported modules to a dict
        for fp in filepaths:
            classes = _import_model_classes_from_file(fp)
            for cls in classes:
                self.model_dict[cls.__name__] = cls

        self.logger.info(
            f'Imported {len(self.model_dict)} SQLAlchemy models:'
            f'\n{pformat(list(self.model_dict.keys()))}'
        )

    def _build_data_dict(self):
        self.logger.info('Build Gen3 data dictionary from SqlAlchemy models')

        self._import_models()
        for model_cls_name, model_cls in self.model_dict.items():
            self._model_to_data_dict()
        return {}

    def _model_to_data_dict(self, model_cls, data_dict):
        pass
