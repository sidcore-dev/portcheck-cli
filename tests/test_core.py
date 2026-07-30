import socket
import threading
import unittest
from unittest.mock import patch

from portcheck_cli.core import check_port, parse_target


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestParseTarget(unittest.TestCase):
    def test_parses_host_and_port(self) -> None:
        host, port = parse_target("example.com:443")
        self.assertEqual(host, "example.com")
        self.assertEqual(port, 443)

    def test_parses_ipv6_bracket_form(self) -> None:
        host, port = parse_target("[::1]:8080")
        self.assertEqual(host, "::1")
        self.assertEqual(port, 8080)

    def test_rejects_missing_colon(self) -> None:
        with self.assertRaises(ValueError):
            parse_target("example.com")

    def test_rejects_non_numeric_port(self) -> None:
        with self.assertRaises(ValueError):
            parse_target("example.com:abc")

    def test_rejects_out_of_range_port(self) -> None:
        with self.assertRaises(ValueError):
            parse_target("example.com:70000")


class TestCheckPort(unittest.TestCase):
    def test_open_port(self) -> None:
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
            result = check_port("127.0.0.1", port, timeout=2.0)
            self.assertEqual(result.status, "open")
        finally:
            server.close()
            thread.join(timeout=1)

    def test_closed_port(self) -> None:
        port = _free_port()
        result = check_port("127.0.0.1", port, timeout=1.0)
        self.assertEqual(result.status, "closed")

    def test_dns_resolution_error(self) -> None:
        with patch("portcheck_cli.core.socket.create_connection", side_effect=socket.gaierror("boom")):
            result = check_port("this-host-should-not-resolve.invalid", 80, timeout=1.0)
        self.assertEqual(result.status, "error")

    def test_timeout(self) -> None:
        with patch("portcheck_cli.core.socket.create_connection", side_effect=TimeoutError()):
            result = check_port("127.0.0.1", 9, timeout=0.1)
        self.assertEqual(result.status, "closed")


if __name__ == "__main__":
    unittest.main()
