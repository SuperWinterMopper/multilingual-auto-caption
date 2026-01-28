import requests
def main():
    ENDPOINT = "https://mu-d68e0144d9624aadb19f02da2628c6e5.ecs.us-east-2.on.aws/presigned"
    
    response: requests.Response = requests.get(
        url=ENDPOINT,
        params={"filename": "test_video.mp4"}
    )

    print("Status:", response.status_code)
    print("Response headers:", response.headers)
    print("Body:", response.text)


if __name__ == '__main__':
    main()