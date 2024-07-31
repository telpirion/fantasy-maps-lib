from google.cloud import firestore

import json


def store_metadata_fs(*, project_id, series, collection_name, uid):
    """Upserts image metadata into a Firestore collection.

    Arguments:
        project_id (str): the Google Cloud project to store these in
        series (pd.Series): a Pandas series with the image's metadata
        collection_name (str): the Firestore collection to store the data in
    """

    client = firestore.Client(project=project_id)

    series_dict = series.to_dict()

    # clean up the data a little bit before upserting
    vtt = series["VTT"]
    if vtt != "":
        vtt = json.loads(vtt)
        series_dict["VTT"] = vtt

    bboxes = series["BBoxes"]
    if bboxes != "":
        bboxes = json.loads(bboxes)["bboxes"]
        series_dict["BBoxes"] = bboxes

    file_name = series["Path"].split("/")[-1]
    series_dict.pop("Path", None)
    series_dict["filename"] = file_name

    img_gcs_uri = series["GCS URI"]
    series_dict.pop("GCS URI", None)
    series_dict["gcsURI"] = img_gcs_uri

    # upsert the dict directly into Firestore!
    client.collection(collection_name).document(uid).set(series_dict)
