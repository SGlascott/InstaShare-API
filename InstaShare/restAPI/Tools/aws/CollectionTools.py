import boto3
from botocore.client import Config
from ..DevOps.credentials import get_credentials
import datetime

creds = get_credentials()
bucket_name = creds.get('bucket')
ACCESS_KEY_ID = creds.get('access')
ACCESS_SECRET_KEY = creds.get('secret')

# "creating a collection" function takes user_id as parameter
# and creates a collection
# returns a newly created collection's id / name
def creating_a_collection(user_id):
    collection_id = str(datetime.datetime.now()) + '_' + str(user_id)
    collection_id = collection_id.replace(' ', '_')
    collection_id = collection_id.replace('.', '_')
    collection_id = collection_id.replace(':', '_')
    collection_id = collection_id.replace('-', '_')
    client = boto3.client('rekognition')

    # Create a collection
    client.create_collection(CollectionId=collection_id)

    return collection_id

# "upload image to AWS" function takes user_id and image as parameters
# and uploads an image to AWS bucket
# returns uploaded image's name that is stored on the AWS S3 bucket

#Changed user_id to contact_id because user_id would produce same file names for every contact.
def upload_image_to_AWS(user_id, image):
    try:
        s3.create_bucket(Bucket=bucket_name)
    except:
        pass

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
    resp = s3.Bucket(bucket_name).put_object(Key=image_name, Body=image)
    # for testing
    #print("Done uploading")

    return image_name

# "adding faces to a collection" function takes user_id, collection_id, image as parameters
# and adds those faces to the collection
# returns a list of face ids that is in the image
def adding_faces_to_a_collection(user_id, collection_id, image, contact=False):
    # Uploading image to AWS bucket
    image_name = upload_image_to_AWS(user_id, image)
    external_image_id = image_name
    client = boto3.client('rekognition')

    if contact == True:
        detect_faces_response = client.detect_faces(Image={'S3Object': {'Bucket': bucket_name, 'Name': image_name}},
                                                    Attributes=['ALL'])
        number_of_faces = 0
        for faceDetail in detect_faces_response['FaceDetails']:
            number_of_faces = number_of_faces + 1

        if (number_of_faces == 0) or (number_of_faces > 1):
            return -1

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

    # for testing
    # print("Done adding_faces_to_a_Collection")

    return list_of_face_ids


# "deleting faces from a collection" function takes collection_id and faces_added_to_collection as parameters
# and deletes the faces added to collection from the user's collection
# (i.e. not user's contact image)
# returns N/A
def deleting_faces_from_a_Collection(collection_id, faces_added_to_collection):
    client = boto3.client('rekognition')
    client.delete_faces(CollectionId=collection_id,
                        FaceIds=faces_added_to_collection)
    # for testing
    # print('Done deleting faces')


# "deleting_a_Collection" function takes collection_id as parameters
# and deletes a user's collection
# returns True is if it is successful, otherwise returns False
def deleting_a_Collection(collection_id):
    client = boto3.client('rekognition')
    statusCode = ''
    try:
        response = client.delete_collection(CollectionId=collection_id)
        statusCode = response['StatusCode']
        print('Operation returned Status Code: ' + str(statusCode))
        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print('The collection ' + collection_id + ' was not found ')
        else:
            print('Error other than Not Found occurred: ' + e.response['Error']['Message'])
        statusCode = e.response['ResponseMetadata']['HTTPStatusCode']
        print('Operation returned Status Code: ' + str(statusCode))
        return False
