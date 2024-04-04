import requests
import json


def run_dash_test():
    # Step 1: Discover the closest M-Lab server using mlab-ns
    mlab_server = "https://locate.measurementlab.net/v2/nearest/ndt"
    closest_server_url = requests.get(mlab_server).json().get("url")

    if closest_server_url is None:
        print("Error: Failed to discover closest M-Lab server")
        return

    # Step 2: Establish a persistent HTTP connection with the server
    session = requests.Session()

    # Step 3: Set the initial estimated rate
    initial_rate = 3000  # kbit/s
    rate_estimate = initial_rate

    # Step 4: For each segment in the emulated video
    for segment_number in range(15):
        # Step 4.1: Request the next segment encoded at the previously estimated rate
        segment_url = f"{closest_server_url}/dash/download/{rate_estimate}"
        response = session.get(segment_url)

        # Step 4.2: Measure the speed at which the segment was downloaded
        speed = response.elapsed.total_seconds()  # Speed is measured in seconds for simplicity

        # Step 4.3: Update the rate estimate (This is simplified)
        rate_estimate = speed  # In a real implementation, you would use a more sophisticated mechanism

        # Step 4.4: Record data for this segment
        segment_data = {
            "iteration": segment_number,
            "connect_time": response.elapsed.total_seconds(),  # Assuming connect time is same as elapsed
            "elapsed": response.elapsed.total_seconds(),
            "elapsed_target": 2,  # Target duration of a segment
            "rate": rate_estimate,  # Bitrate of the segment
            "received": len(response.content),  # Number of bytes received
            "server_url": segment_url,
            "timestamp": int(response.elapsed.total_seconds()),  # Current timestamp
            "version": "0.008000000",  # Version of the experiment
            "platform": "darwin"  # Platform information (can be obtained dynamically)
        }

        # Do something with segment_data, such as saving to a list or sending to a server

    # After all segments have been processed
    # Calculate summary statistics
    median_bitrate = sum(segment_data["rate"] for segment_data in receiver_data) / len(receiver_data)
    connect_latency = sum(segment_data["connect_time"] for segment_data in receiver_data) / len(receiver_data)

    # Prepare simple output
    simple_output = {
        "median_bitrate": median_bitrate,
        "connect_latency": connect_latency
    }

    # Print or return the output
    print(json.dumps(simple_output, indent=2))


# Run the DASH test
run_dash_test()
