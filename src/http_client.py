from dataclasses import dataclass
import http.client
import time


class Client:
    def __init__(self, database):
        self.db = database

        self.endpoints = {}

    def request(self, method: str, path: str, body: str | None = None):
        # Create a connection to the server
        enabled = self.db["http_enabled"]
        host = self.db["host"]
        port = self.db["port"]

        if enabled:
            try:
                conn = http.client.HTTPConnection(host, port, timeout=3)

                # Make a request to the server
                conn.request(method, path, body)

                # Get the response from the server
                response = conn.getresponse()

                # Print the status and reason
                print(f"{method}:{host}{path}::{port} -- {body} "
                      f"=> ({response.status}) {response.reason}")

                # Read and print the response body
                response_body = response.read().decode()
                if response_body:
                    print("Response body:", response_body)

                # Close the connection
                conn.close()

                return response_body
            except TimeoutError:
                print("Connection timed out.")
                return None
            except OSError:
                print("OS Error: Can't Connect to Network.")
        else:
            print(f"[mock]{method}: {host}{path}::{port} -- {body}")
            return None

    def set_timeout(self, time_s: int):
        """
        Send a message to the slave device to set the timeout parameter.
        This is the keep-alive timeout for the furnace microcontroller.
        The furnace microcontroller disables itself if an
        enable POST isn't continuously sent faster than the timeout.
        """
        return self.request("POST", "/api/cooling/timeout", str(time_s))


if __name__ == "__main__":

    c = Client({"host": "10.0.0.10", "port": 80, "http_enabled": True})
    while True:
        c.request("GET", "/api/cooling/status")
        time.sleep(3)
