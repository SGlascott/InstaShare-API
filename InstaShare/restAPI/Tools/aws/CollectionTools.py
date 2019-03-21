import boto3
from botocore.client import Config

bucket_name = 'instashare-images'
ACCESS_KEY_ID = 'AKIAJZOS6BDZWQF4TG2Q'
ACCESS_SECRET_KEY = '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'

# "creating a collection" function takes user_id as parameter
# and creates a collection
# returns a newly created collection's id / name
def creating_a_collection(user_id):
    collection_id = 'Collection-' + str(user_id)
    client = boto3.client('rekognition')

    # Create a collection
    client.create_collection(CollectionId=collection_id)

    return collection_id

# "upload image to AWS" function takes user_id and image as parameters
# and uploads an image to AWS bucket
# returns uploaded image's name that is stored on the AWS S3 bucket

#Changed user_id to contact_id because user_id would produce same file names for every contact.
def upload_image_to_AWS(user_id, image):
    image_name = 'image-' + str(user_id) + '.jpg'

    s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
    s3.Bucket(bucket_name).put_object(Key=image_name, Body=image)

    # for testing
    #print("Done uploading")

    return image_name

# "adding faces to a collection" function takes user_id, collection_id, image as parameters
# and adds those faces to the collection
# returns a list of face ids that is in the image
def adding_faces_to_a_collection(user_id, collection_id, image):

    # Uploading image to AWS bucket
    image_name = upload_image_to_AWS(user_id, image)

    external_image_id = image_name
    client = boto3.client('rekognition')
    response = client.index_faces(CollectionId=collection_id,
                                    Image={'S3Object': {'Bucket': bucket_name, 'Name': image_name}},
                                    ExternalImageId=external_image_id,
                                    MaxFaces=100,
                                    QualityFilter="AUTO",
                                    DetectionAttributes=['ALL'])
    face_ids = []
    for faceRecord in response['FaceRecords']:
        face_ids.append(faceRecord['Face']['FaceId'])

    # striping face_ids
    list_of_face_ids = []
    n = 0
    for i in face_ids:
        temp = i.strip("'")
        list_of_face_ids.append(temp)
        n += 1

    # for testing
    #print("Done adding_faces_to_a_Collection")

    return list_of_face_ids[0]