import boto3
from botocore.client import Config

from . import CollectionTools 
from ..DevOps.credentials import get_credentials

creds = get_credentials()
bucket_name = creds.get('bucket')
ACCESS_KEY_ID = creds.get('access')
ACCESS_SECRET_KEY = creds.get('secret')
# "deleting faces from a collection" function takes collection_id and faces_added_to_collection as parameters
# and deletes the faces added to collection from the user's collection
# (i.e. not user's contact image)
# returns N/A
def deleting_faces_from_a_Collection(collection_id, faces_added_to_collection):

    client = boto3.client('rekognition')
    client.delete_faces(CollectionId=collection_id,
                                   FaceIds=faces_added_to_collection)
    # for testing
    #print('Done deleting faces')

# "searching for a face using its face id" function takes collection_id and list_of_face_ids as parameters
# and does a search for a face in the collection
# it compares all faces from list_of_face_ids to user's collection
# returns a list of face ids that is in the user's contact
def searching_for_a_face_using_its_face_ID(collection_id, list_of_face_ids):
    threshold = 80
    maxFaces = 1

    client = boto3.client('rekognition')

    matched_face_id_list = []
    for face_id in list_of_face_ids:
        response = client.search_faces(CollectionId=collection_id,
                                        FaceId=face_id,
                                        FaceMatchThreshold=threshold,
                                        MaxFaces=maxFaces)

        # striping face_id from respond
        face_matches = response['FaceMatches']
        for match in face_matches:
            striped_id = (match['Face']['FaceId']).strip("'")
            matched_face_id_list.append(striped_id)

    # for testing
    #print("Done searching_for_a_face_using_its_face_ID")
    deleting_faces_from_a_Collection(collection_id, list_of_face_ids)

    return matched_face_id_list

def search_faces_by_image(user_id, group_photo, collection_id, threshold=80):
    image_name = CollectionTools.upload_image_to_AWS(user_id, group_photo)
    #print(image_name)
    rekognition = boto3.client("rekognition")
    response = rekognition.index_faces(
		Image={
			"S3Object": {
				"Bucket": bucket_name,
				"Name": image_name,
			}
		},
		CollectionId=collection_id,
        MaxFaces=15,
	)
    if response['FaceRecords'] == []:
        return []
    #print(get_faces(response['FaceRecords']))
    faces_arr = []
    for id in get_faces(response['FaceRecords']):
        matched_face = rekognition.search_faces(
            CollectionId=collection_id,
            MaxFaces=15,
            FaceId=id,
            FaceMatchThreshold=threshold
        )
        #print(matched_face)
        if matched_face['FaceMatches'] != []:
            faces_arr.append(matched_face['FaceMatches'][0].get('Face').get('FaceId'))


    deletion = rekognition.delete_faces(CollectionId=collection_id,
                               FaceIds=get_faces(response['FaceRecords']))       
    return faces_arr

def get_faces(FaceRecords):
    face_ids = []
    for i in FaceRecords:
        face_ids.append(str(i.get('Face').get('FaceId')).replace(' ', ''))
    return face_ids
