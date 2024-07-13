import http.client
import time

# Define the server and port
server = "10.0.0.83"
port = 80

class Client:
    def __init__(self, host, port, mock=True)
        self.host = host
        self.port = port


    def request(self, method: str, path: str, body: str | None = None):
        # Create a connection to the server
        if not self.mock:
            conn = http.client.HTTPConnection(server, port)

            # Make a request to the server
            conn.request(method, path, body)

            # Get the response from the server
            response = conn.getresponse()

            # Print the status and reason
            print(
                f"{method}:{path} -- {body} => ({response.status}) {response.reason}")
            # print("Body:", body)
            # print("Status:", response.status)
            # print("Reason:", response.reason)

            # Read and print the response body
            response_body = response.read().decode()
            if response_body:
                print("Response body:", response_body)

            # Close the connection
            conn.close()
        else:
            print(
                f"{method}:{path} -- {body} => ({response.status}) {response.reason}")

        return response_body


    enable_cooling = lambda: request("POST", "/api/cooling/status", "enable")
    disable_cooling = lambda: request("POST", "/api/cooling/status", "disable")


    def set_timeout(time_s: int):
        return request("POST", "/api/cooling/timeout", str(time_s))


if __name__ == "__main__":
    TIMEOUT_S = 15
    POLL_RATE_S = 5

    set_timeout(TIMEOUT_S)

    while True:
        enable_cooling()

        # Sleep rate should be at least half of timeout.
        time.sleep(POLL_RATE_S)

    disable_cooling()
