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

    def __init__(self, host, port, enabled=True):
        self.host = host
        self.port = port
        self.enabled = enabled

        self.endpoints = {}

        self.mutex = threading.Lock()

    # def register_endpoint(self, name, method, path, body=None):
    #     self.endpoints[name] = Request(method, path, body)

    def set_host(self, host):
        with self.mutex:
            self.host = host

    def set_port(self, port):
        with self.mutex:
            self.port = port
    def enable(self):
        with self.mutex:
            self.enabled = not self.enabled
            print(f"HTTP Enabled: {self.enabled}")

    def request(self, method: str, path: str, body: str | None = None):
        # Create a connection to the server
        with self.mutex:
            if self.enabled:
                try:
                    conn = http.client.HTTPConnection(self.host, self.port, timeout=3)

                    # Make a request to the server
                    conn.request(method, path, body)

                    # Get the response from the server
                    response = conn.getresponse()

                    # Print the status and reason
                    print(
                        f"{method}:{self.host}{path}::{self.port} -- {body} => ({response.status}) {response.reason}"
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
                print(f"[mock]{method}: {self.host}{path}::{self.port} -- {body}")
                return None

    def set_timeout(self, time_s: int):
        return self.request("POST", "/api/cooling/timeout", str(time_s))


if __name__ == "__main__":

    c = Client("10.0.0.83", 80, mock=False)
    while True:
        c.request("GET", "/api/cooling/status")
        time.sleep(3)
