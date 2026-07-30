import socket
import threading
import unittest
from unittest.mock import patch

from portcheck_cli.cli import main


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestCli(unittest.TestCase):
    def test_open_port_exit_0(self) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        def accept_once() -> None:
            try:
                conn, _ = server.accept()
                conn.close()
            except OSError:
                pass

        thread = threading.Thread(target=accept_once, daemon=True)
        thread.start()
        try:
            code = main([f"127.0.0.1:{port}", "--timeout", "2"])
            self.assertEqual(code, 0)
        finally:
            server.close()
            thread.join(timeout=1)

    def test_closed_port_exit_1(self) -> None:
        port = _free_port()
        code = main([f"127.0.0.1:{port}", "--timeout", "1"])
        self.assertEqual(code, 1)

    def test_invalid_target_exit_2(self) -> None:
        code = main(["not-a-valid-target"])
        self.assertEqual(code, 2)

    def test_dns_error_exit_2(self) -> None:
        with patch("portcheck_cli.cli.check_port") as mock_check:
            from portcheck_cli.core import PortCheckResult

            mock_check.return_value = PortCheckResult("error", "could not resolve host")
            code = main(["bad.invalid:80"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
