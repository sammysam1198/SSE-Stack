from utils.r2_utils import upload_bytes_to_r2

upload_bytes_to_r2(
    data=b"hello world",
    object_key="test/test.txt",
    content_type="text/plain"
)