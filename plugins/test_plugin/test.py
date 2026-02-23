from snowx.plugins.lazy_init import on_lazy_init
from snowx.api.plugin import get_id_from_stack


@on_lazy_init
def test_domain():
    print("before test domain")

    print(get_id_from_stack())

    print("after test domain")
