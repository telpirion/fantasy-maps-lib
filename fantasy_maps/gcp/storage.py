from google.cloud import storage


def store_image_gcs(*, project_id, series, bucket_name, prefix):
    """Copies a local image to Google Cloud Storage.

    Arguments:
        project_id (str): the Google Cloud Project ID to use
        series (pd.Series): a Pandas Series with "Path" column
        bucket_name (str): the Cloud Storage bucket to use
        prefix (str): the prefix or "folder" to use in the bucket

    Returns:
        String. The Cloud Storage URI of the image.
    """

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)

    local_path = series["Path"]
    file_name = local_path.split("/")[-1]
    img_gcs_uri = f"gs://{bucket_name}/{prefix}/{file_name}"
    blob_name = f"{prefix}/{file_name}"

    file_blob = bucket.blob(blob_name)
    file_blob.upload_from_filename(local_path)

    return img_gcs_uri
