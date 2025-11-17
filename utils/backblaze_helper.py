# utils/backblaze_helper.py
import tempfile
import os
import traceback
from typing import Optional

def robust_download(bucket, api, cloud_filename: str) -> Optional[bytes]:
    """
    Try multiple common Backblaze SDK download patterns and return raw bytes.
    Accepts either a bucket object (preferred) or an api object.
    """
    temp_path = None
    try:
        # Strategy A: bucket.download_file_by_name(name, dest_path)
        if bucket is not None and hasattr(bucket, "download_file_by_name"):
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    temp_path = tmp.name
                try:
                    bucket.download_file_by_name(cloud_filename, temp_path)
                    with open(temp_path, "rb") as f:
                        return f.read()
                except TypeError:
                    res = bucket.download_file_by_name(cloud_filename)
                    if isinstance(res, (bytes, bytearray)):
                        return bytes(res)
                    if hasattr(res, "read"):
                        return res.read()
                    try:
                        return b"".join(list(res))
                    except Exception:
                        pass
            except Exception:
                pass

        # Strategy B: get file_info then api.download_file_by_id(file_id, dest)
        try:
            file_info = None
            if bucket is not None and hasattr(bucket, "get_file_info_by_name"):
                try:
                    file_info = bucket.get_file_info_by_name(cloud_filename)
                except Exception:
                    file_info = None

            file_id = None
            if file_info is not None:
                file_id = getattr(file_info, "file_id", None) or getattr(file_info, "id_", None) or getattr(file_info, "id", None)

            if file_id and api is not None:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    temp_path = tmp.name
                try:
                    if hasattr(api, "download_file_by_id"):
                        api.download_file_by_id(file_id, temp_path)
                        with open(temp_path, "rb") as f:
                            return f.read()
                except Exception:
                    pass

                try:
                    if hasattr(bucket, "download_file_by_id"):
                        bucket.download_file_by_id(file_id, temp_path)
                        with open(temp_path, "rb") as f:
                            return f.read()
                except Exception:
                    pass
        except Exception:
            pass

        # Strategy C: bucket.download_file_by_name() returns bytes/stream/iterable
        try:
            if bucket is not None and hasattr(bucket, "download_file_by_name"):
                maybe = bucket.download_file_by_name(cloud_filename)
                if isinstance(maybe, (bytes, bytearray)):
                    return bytes(maybe)
                if hasattr(maybe, "getvalue"):
                    return maybe.getvalue()
                if hasattr(maybe, "read"):
                    return maybe.read()
                try:
                    return b"".join(list(maybe))
                except Exception:
                    pass
        except Exception:
            pass

        return None

    except Exception as e:
        print("robust_download exception:", e)
        traceback.print_exc()
        return None
    finally:
        try:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception:
            pass
