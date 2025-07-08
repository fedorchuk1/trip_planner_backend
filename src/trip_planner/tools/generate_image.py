import os
import requests

url = "https://api.getimg.ai/v1/flux-schnell/text-to-image"
BEARER_KEY = os.environ.get("GETIMG_API_KEY")


def generate_image(
    image_prompt: str,
    height: int = 512,
    width: int = 1024,
    steps: int = 4,
    output_format: str = "jpeg",
    response_format: str = "b64"
) -> str:
    payload = {
        "prompt": image_prompt,
        "height": height,
        "width": width,
        "steps": steps,
        "output_format": output_format,
        "response_format": response_format,
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {BEARER_KEY}"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()["image"]


