import boto3
from botocore.client import Config

from . import CollectionTools 
from ..DevOps.credentials import get_credentials

# creds = get_credentials()
# bucket_name = creds.get('bucket')
# ACCESS_KEY_ID = creds.get('access')
# ACCESS_SECRET_KEY = creds.get('secret')
bucket_name = 'instashare-images'
ACCESS_KEY_ID = 'AKIAIEYW22STVFAHO2DA'
ACCESS_SECRET_KEY = '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'

# "search faces by image" function takes group_photo, collection_id,
# threshold as parameter and searches faces by image
# returns a newly created collection's id if it is successful,
# otherwise prints an error message
def search_faces_by_image(user_id, group_photo, collection_id, threshold=80):

    list_of_face_ids = CollectionTools.adding_faces_to_a_collection(user_id, collection_id, group_photo)
    rekognition = boto3.client('rekognition')

    try:
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
                break
    except ClientError:
        print('An error occurred when doing search faces')
        return -1

    CollectionTools.deleting_faces_from_a_Collection(collection_id, list_of_face_ids)
    return matched_face_ids