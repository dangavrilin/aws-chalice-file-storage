# aws-chalice-file-storage

A chalice based simple API for adding and removing image files from AWS S3 Bucket.

## Setup

Note: Make sure you installed and configured [chalice](https://github.com/aws/chalice) and [aws-cli](https://github.com/aws/aws-cli).

### CloudFormation Resources

A CloudFormation template provisions all the resources needed for the application:
* S3 Bucket for storing files
* DynamoDB for indexing stored files

Create the CloudFormation stack using the AWS CLI:

```bash
aws cloudformation create-stack --stack-name aws-chalice-file-storage --template-body file://cloudformation.json 
```

### Chalice Application

File `.chalice/policy-dev.json` contains all requirement policies. The only thing you need to is to deploy your application:

```
$ chalice deploy
```

### Create an API Key

Create an API key for API Gateway endpoint to be used by the user
interface for secure access.

## API v1 endpoints 

* [Get images](#get-images) 
* [Add image](#add-image) 
* [Remove image/gallery](#remove-image) 

#### Get images
  
  Returns list of files' urls in the collection.

* **URL**

  /v1/images?userId=[userId]&collectionId=[collectionId]

* **Method:**

  `GET`
  

*  **Params**

   **Required:**
 
    `userId=[integer]`
    example: `userId=1`
   
    `collectionId=[integer]`
    example: `collectionId=2`
	

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:**
```json
{
    "gallery:": [
        {
            "href": "www.example.com/fcbcc116-d818-4da4-8b9b-585b3e3c92a4.jpg",
            "primary": true
        },
        {
            "href": "www.example.com/1cfb1ab6-b5ea-4756-8565-78987b17a58b.jpg",
            "primary": false
        }
    ]
}
```
 
* **Error Response:**

  * **Code:** 403 FORBIDDEN
  
* **Sample request:**
    
```bash
curl --request GET \
  --url 'www.example.com/api/v1/images?userId=1&collectionId=1' \
```

#### Add image
  
  Add image into the collection.

* **URL**

  /v1/images?userId=[userId]&collectionId=[collectionId]

* **Method:**

  `POST`
  

*  **Params**

   **Required:**
 
    `userId=[integer]`
    example: `userId=1`
   
    `collectionId=[integer]`
    example: `collectionId=2`
	
*  **Headers**
   
   **Required:** 
	
	`Content-Type: application/octet-stream`

* **Body**

  **Required:**
  
  *.jpg binary file

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:**
```json
{
    "message": "Upload successful"
}
```
 
* **Error Response:**

  * **Code:** 403 FORBIDDEN
  
* **Sample request:**
    
```bash
curl --request POST \
  --url 'www.example.com/api/v1/images?userId=1&collectionId=1' \
  --header 'Content-Type: application/octet-stream'
```

#### Remove image
  
Remove an image or whole gallery.

* **URL**

  Delete an image:
  /v1/images?userId=[userId]&collectionId=[collectionId]&position=[position]

	Delete a category:
	/v1/images?userId=[userId]&collectionId=[collectionId]

* **Method:**

  `DELETE`

*  **Params**

   **Required:**
 
    `userId=[integer]`
    example: `userId=1`
   
    `collectionId=[integer]`
    example: `collectionId=2`
  
  **Optional:**
  
	`position=[integer]`
	example: `position=1`

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:**
```json
{
    "message": "Collection/file has been removed"
}
```
 
* **Error Response:**

  * **Code:** 403 FORBIDDEN 
  
* **Sample request:**
    
```bash
curl --request DELETE \
  --url 'www.example.com/api/v1/images?userId=1&collectionId=1&position=1' \
```

