import boto3
from botocore.client import Config
from ..DevOps.credentials import get_credentials
import datetime
from botocore.exceptions import ClientError

creds = get_credentials()
bucket_name = creds.get('bucket')
ACCESS_KEY_ID = creds.get('access')
ACCESS_SECRET_KEY = creds.get('secret')

# "creating a collection" function takes user_id as parameter
# and creates a collection
# returns a newly created collection's id if it is successful,
# otherwise prints an error message
def creating_a_collection(user_id):
    collection_id = str(datetime.datetime.now()) + '_' + str(user_id)
    collection_id = collection_id.replace(' ', '_')
    collection_id = collection_id.replace('.', '_')
    collection_id = collection_id.replace(':', '_')
    collection_id = collection_id.replace('-', '_')
    client = boto3.client('rekognition')

    # Create a collection
    try:
        client.create_collection(CollectionId=collection_id)
        return collection_id
    except ClientError:
        print('An error occurred when creating a collection')


# "upload image to AWS" function takes user_id and image as parameters
# and uploads an image to AWS bucket
# returns uploaded image's name that is stored on the AWS S3 bucket
# if it is successful, otherwise prints an error message
def upload_image_to_AWS(user_id, image):
    image_name = str(datetime.datetime.now()) + '_' + str(user_id)
    image_name = image_name.replace(' ', '_')
    image_name = image_name.replace('.', '_')
    image_name = image_name.replace(':', '_')
    image_name = image_name.replace('-', '_')
    image_name = image_name  + '.jpg'

    s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )

    try:
        s3.Bucket(bucket_name).put_object(Key=image_name, Body=image)
        return image_name
    except ClientError:
        print('An error occurred when uploading an image to AWS')


# "adding faces to a collection" function takes user_id, collection_id,
# image and contact flag as parameters and adds those faces to the collection.
# If contact flag is true, it checks for multiple faces. If there is a one face,
# it returns that contact face id else it returns -1.
# Otherwise it skips checking for multiple faces and returns a list of face ids
# that is in the image. If is not successful doing any of this,
# it prints appropriate error message.
def adding_faces_to_a_collection(user_id, collection_id, image, contact=False):
    # Uploading image to AWS bucket
    image_name = upload_image_to_AWS(user_id, image)
    external_image_id = image_name
    client = boto3.client('rekognition')

    if contact == True:
        try:
            detected_faces = client.detect_faces(Image={'S3Object': {'Bucket': bucket_name, 'Name': image_name}},
                                                    Attributes=['ALL'])
            number_of_faces = 0
            for faceDetail in detected_faces['FaceDetails']:
                number_of_faces = number_of_faces + 1

            if (number_of_faces == 0) or (number_of_faces > 1):
                return -1
        except ClientError:
            print('An error occurred when detecting a face on contact image')

    try:
        response = client.index_faces(CollectionId=collection_id,
                                    DetectionAttributes=['ALL'],
                                    ExternalImageId=external_image_id,
                                    Image={'S3Object': {'Bucket': bucket_name, 'Name': image_name}},
                                    MaxFaces=15,
                                    )
        face_ids = []
        for faceRecord in response['FaceRecords']:
            face_ids.append(faceRecord['Face']['FaceId'])

        # striping face_ids
        list_of_face_ids = []
        for i in face_ids:
            temp = i.strip("'")
            list_of_face_ids.append(temp)
        return list_of_face_ids
    except ClientError:
        print('An error occurred when adding face/faces to collection')

def adding_faces_to_a_collection_android(user_id, collection_id, image, contact=False):
    # Uploading image to AWS bucket
    image_name = upload_image_to_AWS(user_id, image)
    external_image_id = image_name
    client = boto3.client('rekognition')
    url = 'https://s3.amazonaws.com/instashare-images/'

    if contact == True:
        try:
            detected_faces = client.detect_faces(Image={'S3Object': {'Bucket': bucket_name, 'Name': image_name}},
                                                    Attributes=['ALL'])
            number_of_faces = 0
            for faceDetail in detected_faces['FaceDetails']:
                number_of_faces = number_of_faces + 1

            if (number_of_faces == 0) or (number_of_faces > 1):
                return -1
        except ClientError:
            print('An error occurred when detecting a face on contact image')

    try:
        response = client.index_faces(CollectionId=collection_id,
                                    DetectionAttributes=['ALL'],
                                    ExternalImageId=external_image_id,
                                    Image={'S3Object': {'Bucket': bucket_name, 'Name': image_name}},
                                    MaxFaces=15,
                                    )
        face_ids = []
        for faceRecord in response['FaceRecords']:
            face_ids.append(faceRecord['Face']['FaceId'])

        # striping face_ids
        list_of_face_ids = []
        for i in face_ids:
            temp = i.strip("'")
            list_of_face_ids.append(temp)
        dic = dict(face_ids = list_of_face_ids, url = url + image_name)
        return dic
    except ClientError:
        print('An error occurred when adding face/faces to collection')

# "deleting faces from a collection" function takes collection_id and faces_added_to_collection as parameters
# and deletes the faces added to collection from the user's collection
#if it is successful, otherwise prints an error message
def deleting_faces_from_a_Collection(collection_id, faces_added_to_collection):
    client = boto3.client('rekognition')
    try:
        client.delete_faces(CollectionId=collection_id,
                            FaceIds=faces_added_to_collection)
    except ClientError:
        print('An error occurred when deleting faces from a collection')
