import boto3
from botocore.client import Config

from . import CollectionTools 
from ..DevOps.credentials import get_credentials

creds = get_credentials()
bucket_name = creds.get('bucket')
ACCESS_KEY_ID = creds.get('access')
ACCESS_SECRET_KEY = creds.get('secret')

def searching_for_a_face_using_its_face_id(user_id, group_photo, collection_id, threshold=80):

    list_of_face_ids = CollectionTools.adding_faces_to_a_collection(user_id, collection_id, group_photo)
    rekognition = boto3.client('rekognition')

    matched_face_ids = []
    for face_id in list_of_face_ids:
        response = rekognition.search_faces(CollectionId=collection_id,
                                        FaceId=face_id,
                                        FaceMatchThreshold=threshold,
                                        MaxFaces=15)

        # striping face_id from respond
        face_matches = response['FaceMatches']
        for match in face_matches:
            striped_id = (match['Face']['FaceId']).strip("'")
            matched_face_ids.append(striped_id)


    # for testing
    #print("Done searching_for_a_face_using_its_face_ID")
