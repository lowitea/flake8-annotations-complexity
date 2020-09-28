from typing import Generator, Tuple

from flake8_annotations_complexity import __version__ as version, validators
from flake8_annotations_complexity.ast_helpres import get_annotation_nodes


class AnnotationsChecker:
    name = 'flake8-annotations-complexity'
    version = version

    max_annotations_complexity = None
    default_max_annotations_complexity = 3

    max_annotations_len = None
    default_max_annotations_len = 7

    enable_old_style = None
    default_enable_old_style = False

    def __init__(self, tree, filename: str):
        self.filename = filename
        self.tree = tree

        if AnnotationsChecker.max_annotations_complexity is None:
            AnnotationsChecker.max_annotations_complexity = self.default_max_annotations_complexity
        if AnnotationsChecker.max_annotations_len is None:
            AnnotationsChecker.max_annotations_len = self.default_max_annotations_len
        if AnnotationsChecker.enable_old_style is None:
            AnnotationsChecker.enable_old_style = self.default_enable_old_style

    @classmethod
    def add_options(cls, parser) -> None:
        parser.add_option(
            '--max-annotations-complexity',
            type=int,
            parse_from_config=True,
            default=cls.default_max_annotations_complexity,
        )
        parser.add_option(
            '--max-annotations-len',
            type=int,
            parse_from_config=True,
            default=cls.default_max_annotations_len,
        )
        parser.add_option(
            '--enable-old-style-annotations',
            type=bool,
            parse_from_config=True,
            default=cls.default_enable_old_style,
        )

    @classmethod
    def parse_options(cls, options) -> None:
        cls.max_annotations_complexity = int(options.max_annotations_complexity)
        cls.max_annotations_len = int(options.max_annotations_len)
        cls.enable_old_style = bool(options.enable_old_style_annotations)

    def get_validators(self) -> Tuple[validators.Validator, ...]:
        enabled_validators: Tuple[validators.Validator, ...] = (
            validators.AnnotationComplexity(self.max_annotations_complexity),  # type: ignore
            validators.AnnotationLength(self.max_annotations_len),  # type: ignore
        )
        if self.enable_old_style is False:
            enabled_validators += (validators.AnnotationOldStyle(),)
        return enabled_validators

    def run(self) -> Generator[Tuple[int, int, str, type], None, None]:
        bad_annotations = []
        annotations = get_annotation_nodes(self.tree)

        for annotation in annotations:
            for validator in self.get_validators():
                msg = validator.validate(annotation)
                if msg:
                    bad_annotations.append((annotation, msg))

        for annotation, error_msg in bad_annotations:
            yield (
                annotation.lineno,
                annotation.col_offset,
                error_msg,
                type(self),
            )
