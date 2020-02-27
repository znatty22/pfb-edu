"""
Transform SQLAlchemy Models to PFB Schema
"""
import os
import logging
import inspect
import subprocess
from collections import defaultdict
import timeit
from pprint import pformat

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.inspection import inspect as sqla_inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.exc import NoInspectionAvailable

from pfb_exporter.utils import import_module_from_file, seconds_to_hms
from pfb_exporter.transform.base import Transformer

SQLA_AVRO_TYPE_MAP = {
    'primitive': {
        'Text': 'string',
        'Boolean': 'boolean',
        'Float': 'float',
        'Integer': 'int',
        'String': 'string',
        'UUID': 'string',
        'DateTime': 'string',
    },
    'logical': {
        'UUID': 'uuid',
        'DateTime': None
    }
}


class SqlaTransformer(Transformer):

    def __init__(self, models_filepath, output_dir, db_conn_url=None):
        """
        Constructor

        :param models_filepath: path to where the SQLAlchemy models are stored
        or will be written if they are generated
        :type models_filepath: str
        :param output_dir: path where PFB Schema will be written
        :type output_dir: str
        :param db_conn_url: Connection URL for database. Format depends on
        database. See SQLAlchemy documentation for supported databases
        """

        super().__init__(models_filepath, output_dir)
        self.logger = logging.getLogger(type(self).__name__)
        self.db_conn_url = db_conn_url
        self.data_dict = {}
        self.model_dict = {}

    def _transform(self):
        """
        Entry point for PFB schema generation.

        Called by pfb_exporter.transform.base.Transformer

        1. (Optional) Generate SQLAlchemy models from database
        2. Import model classes from dir or file
        2. Transform SQLAlchemy models to PFB Schema
        """
        self.logger.info('Build PFB Schema from SqlAlchemy models')

        if self.db_conn_url:
            self._generate_models()

        self._import_models()

        if not (self.db_conn_url or self.model_dict):
            raise RuntimeError(
                'There are 0 models to generate the PFB file. You must '
                'provide a DB connection URL that can be used to '
                'connect to a database to generate the models or '
                'provide a dir or file path to where the models reside'
            )

        return self._create_pfb_schema()

    def _generate_models(self):
        """
        Generate SQLAlchemy models from database

        Uses sqlacodegen CLI to generate models
        See https://github.com/agronholm/sqlacodegen
        """
        # sqlacodegen requires the models to be written to a file
        if os.path.isdir(self.models_filepath):
            self.models_filepath = os.path.join(
                self.models_filepath, 'models.py'
            )

        # Generate SQLAlchemy models
        cmd_str = (
            f'sqlacodegen {self.db_conn_url} --outfile {self.models_filepath}'
        )
        self.logger.debug(f'Building SQLAlchemy models:\n{cmd_str}')

        start_time = timeit.default_timer()
        output = subprocess.run(
            cmd_str, shell=True, stdout=subprocess.PIPE
        )
        total_time = timeit.default_timer() - start_time

        output.check_returncode()

        self.logger.debug(f'Time elapsed: {seconds_to_hms(total_time)}')

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

    def _create_pfb_schema(self):
        """
        Transform SQLAlchemy models into PFB schema
        """
        self.logger.info('Creating PFB schema from SQLAlchemy models ...')
        relational_model = {}

        for model_name, model_cls in self.model_dict.items():
            self.logger.info(
                f'Building schema for {model_name} ...'
            )
            # Inspect model columns and types
            for p in sqla_inspect(model_cls).iterate_properties:
                model_schema = defaultdict(list)

                if not isinstance(p, ColumnProperty):
                    continue

                if not hasattr(p, 'columns'):
                    continue

                column_obj = p.columns[0]

                # Check if foreign key
                if column_obj.foreign_keys:
                    fkname = column_obj.foreign_keys.pop().target_fullname
                    model_schema['foreign_keys'].append(
                        {'table': fkname.split('.')[0], 'name': p.key}
                    )

                # Convert SQLAlchemy column type to avro type
                stype = type(column_obj.type).__name__
                # Get avro primitive type
                ptype = SQLA_AVRO_TYPE_MAP['primitive'].get(stype)
                if not ptype:
                    self.logger.warn(
                        f'⚠️ Could not find avro type for {p}, '
                        f'SQLAlchemy type: {stype}'
                    )
                attr_dict = {'name': p.key, 'type': ptype}

                # Get avro logical type if applicable
                ltype = SQLA_AVRO_TYPE_MAP['logical'].get(stype)
                if ltype:
                    attr_dict.update({'logicalType': ltype})

                # Get default value for attr
                # if column_obj.default:
                #     attr_dict.update({'default': column_obj.default})

                # if column_obj.nullable:
                #     attr_dict.update({'nullable': column_obj.nullable})

                model_schema['attributes'].append(attr_dict)

            relational_model[model_cls.__tablename__] = model_schema

        return relational_model
