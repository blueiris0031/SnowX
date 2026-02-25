from urllib.parse import quote_plus

from ..components.db_url import URLGeneratorManager


_generator_manager = URLGeneratorManager()


def get_db_url(db_type: str, **kwargs: str) -> str:
    generator = _generator_manager.get_generator(db_type)
    base_url = generator(
        **{
            key: quote_plus(value)
            for key, value in kwargs.items()
        }
    )

    return f"{db_type}://{base_url}"
