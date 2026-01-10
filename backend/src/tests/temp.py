from pydantic import AnyHttpUrl
from ..dataclasses.inputs.caption import CaptionInput

x = CaptionInput(
    upload_url = AnyHttpUrl("http://example.com/video.mp4"),   
    convert_to="en"
)

print(x)

print(type(x.upload_url.unicode_string()))