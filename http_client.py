from dataclasses import dataclass
import http.client
import time
import threading


@dataclass
class Request:
    method: str
    path: str
    body = None


class Client:

    def __init__(self, database):
        self.db = database

        self.endpoints = {}

    # def register_endpoint(self, name, method, path, body=None):
    #     self.endpoints[name] = Request(method, path, body)

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
                print(
                    f"{method}:{host}{path}::{port} -- {body} => ({response.status}) {response.reason}"
                )
                # print("Body:", body)
                # print("Status:", response.status)
                # print("Reason:", response.reason)

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
        else:
            print(f"[mock]{method}: {host}{path}::{port} -- {body}")
            return None

    def set_timeout(self, time_s: int):
        return self.request("POST", "/api/cooling/timeout", str(time_s))


if __name__ == "__main__":

    c = Client("esp32s3-therm.local", 80, enabled=True)
    while True:
        c.request("GET", "/api/cooling/status")
        time.sleep(3)
