"""
Entry point for the Kids First PFB Exporter
"""

import click


from pfb_exporter.config import DEFAULT_TRANFORM_MOD, DEFAULT_OUTPUT_DIR
from pfb_exporter.export import PfbExporter

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    A CLI wrapper for running the pfb exporter
    """
    pass


def common_args_options(func):
    """
    Common click args and options
    """
    func = click.option(
        '--output_dir', '-o',
        help='Path to the output directory',
        show_default=True,
        default=DEFAULT_OUTPUT_DIR,
        type=click.Path(exists=False, file_okay=False, dir_okay=True))(func)
    func = click.option(
        '--transform_module', '-t',
        help='Path to the Python module used to transform from a '
        'relational model to the Gen3 data dictionary',
        show_default=True,
        default=DEFAULT_TRANFORM_MOD,
        type=click.Path(exists=True, file_okay=True, dir_okay=False))(func)
    func = click.argument(
        'models_filepath',
        type=click.Path(exists=True, file_okay=True, dir_okay=True))(func)

    return func


@click.command()
@common_args_options
@click.argument('data_dir',
                type=click.Path(exists=True, file_okay=True, dir_okay=True))
def export(data_dir, models_filepath, transform_module, output_dir):
    """
    Export Kids First data to PFB (Portable Bioinformatics Format)

    \b
    Arguments:
        \b
        models_filepath - Path to directory or file containing the SQLAlchemy
        relational model

        data_dir - Path to directory containing the JSON payloads which
        conform to the SQLAlchemy models.
    """
    PfbExporter(
        models_filepath, data_dir, transform_module, output_dir
    ).export()


@click.command()
@common_args_options
def transform(models_filepath, transform_module, output_dir):
    """
    Transform Kids First relational model into a Gen3 data dictionary, which
    is a required input for PFB file creation.

    \b
    Arguments:
        \b
        models_filepath - Path to directory or file containing the sqlalchemy
        models

        data_dir - Path to directory containing the JSON payloads which
        conform to the sqlalchemy models.
    """

    PfbExporter(
        models_filepath, '', transform_module, output_dir
    ).export(output_to_pfb=False)


cli.add_command(export)
cli.add_command(transform)
