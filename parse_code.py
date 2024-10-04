import base64
import io

def parse_code(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        return io.StringIO(decoded.decode('utf-8')).read()
    except Exception as e:
        return f"Error decoding file: {str(e)}"
