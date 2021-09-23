import os
import tempfile
import logging
from google.cloud import storage

from modep_common import settings

logger = logging.getLogger(__name__)

class StorageClient:
    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket(settings.GCP_BUCKET)

    def download(self, gs_path, dest_path=None):
        if dest_path is None:
            _, ext = os.path.splitext(gs_path)
            dest_path = tempfile.NamedTemporaryFile().name + ext
        blob = self.bucket.blob(gs_path)
        blob.download_to_filename(dest_path)
        logger.info(f"Downloaded: '{gs_path}' to '{dest_path}'")
        return dest_path

    def upload(self, src_path, dest_path):
        blob = self.bucket.blob(dest_path)

        # default chunk size of 100 MB can be too big for slow connections
        assert hasattr(blob, 'chunk_size')
        blob.chunk_size = 10 * 1024 * 1024 # 50 MB

        blob.upload_from_filename(src_path)
        logger.info(f"Uploaded: '{src_path}' to '{dest_path}'")

    def delete(self, gs_path):
        blob = self.bucket.blob(gs_path)
        blob.delete()
        logger.info(f"Deleted: '{gs_path}'")
