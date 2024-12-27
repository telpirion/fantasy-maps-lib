from google.cloud import firestore

import json

from fantasy_maps.image.image_metadata import ImageMetadata

def store_metadata_fs(*,
                      project_id: str,
                      img_metadata: ImageMetadata,
                      collection_name: str):
    """Upserts image metadata into a Firestore collection.

    Arguments:
        project_id (str): the Google Cloud project to store these in
        img_metadata (ImageMetadata): the image's metadata
        collection_name (str): the Firestore collection to store the data in
    """

    client = firestore.Client(project=project_id)

    img_dict = img_metadata.to_dict()

    # clean up the data a little bit before upserting
    vtt = img_metadata.to_vtt()
    if vtt != "":
        vtt = json.loads(vtt)
        img_dict["vtt"] = vtt

    file_name = img_metadata.path.split("/")[-1]
    img_dict.pop("path", None)
    img_dict["filename"] = file_name

    # upsert the dict directly into Firestore!
    client.collection(collection_name).document(uid).set(img_dict)

