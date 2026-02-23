import aiomysql
from snowx.plugins import snowx_config
from snowx.api.logger import get_logger


auto_config = snowx_config.auto_config
config = snowx_config.get_config(
    name="mysql_connector",
    host=auto_config("localhost"),
    port=auto_config("3306"),
    user=auto_config("root"),
    password=auto_config("P@ssw0rd"),
    database=auto_config("database"),
    charset=auto_config("utf8"),
)


class Connector:
    def __init__(
            self,
            host: str,
            port: int,
            user: str,
            password: str,
            database: str,
            charset: str = "utf8",
    ):
        self._logger = get_logger(f"MysqlConnector-{host}:{port}")

        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._charset = charset

        self._pool = None

    async def init(self) -> None:
        if self._pool is not None:
            return

        self._logger.info("Connecting to MySQL Server...")
        self._pool = await aiomysql.create_pool(
            maxsize=32,
            pool_recycle=600,

            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            db=self._database,
            charset=self._charset,
            autocommit=True
        )

    async def exit(self) -> None:
        if self._pool:
            self._pool.close()

        self._pool = None
